import re
import yaml
import json
from typing import cast
from datetime import timezone, datetime
from functools import wraps
from pydantic import ValidationError
from .env import ENCODER, LOG, CONFIG, ProfileConfig
from .models.blob import (
    Blob,
    BlobType,
    ChatBlob,
    DocBlob,
    SummaryBlob,
    OpenAICompatibleMessage,
)
from .models.database import GeneralBlob
from .models.response import UserEventData, EventData
from .models.utils import Promise, CODE
from .connectors import get_redis_client, PROJECT_ID

LIST_INT_REGEX = re.compile(r"\[\s*(?:\d+(?:\s*,\s*\d+)*\s*)?\]")


def event_str_repr(event: UserEventData) -> str:
    event_data = event.event_data
    if event_data.event_tip is None:
        profile_deltas = [
            f"- {ed.attributes['topic']}::{ed.attributes['sub_topic']}: {ed.content}"
            for ed in event_data.profile_delta
        ]
        profile_delta_str = "\n".join(profile_deltas)
        return profile_delta_str
    else:
        if event_data.event_tags:
            event_tags = "\n".join(
                [f"- {tag.tag}: {tag.value}" for tag in event_data.event_tags]
            )
        else:
            event_tags = ""
        return f"{event_tags}\n{event_data.event_tip}"


def event_embedding_str(event_data: EventData) -> str:
    if event_data.profile_delta is None:
        profile_delta_str = ""
    else:
        profile_deltas = [
            f"- {ed.attributes['topic']}::{ed.attributes['sub_topic']}: {ed.content}"
            for ed in event_data.profile_delta
        ]
        profile_delta_str = "\n".join(profile_deltas)

    if event_data.event_tags is None:
        event_tags = ""
    else:
        event_tags = "\n".join(
            [f"- {tag.tag}: {tag.value}" for tag in event_data.event_tags]
        )

    if event_data.event_tip is None:
        r = f"{profile_delta_str}\n{event_tags}"
    else:
        r = f"{event_data.event_tip}\n{profile_delta_str}\n{event_tags}"
    return r


def load_json_or_none(content: str) -> dict | None:
    try:
        return json.loads(content)
    except Exception:
        LOG.error(f"Invalid json: {content}")
        return None


def find_list_int_or_none(content: str) -> list[int] | None:
    result = LIST_INT_REGEX.findall(content)
    if not result:
        return None
    result = result[0]
    ids = result.strip("[]").strip()
    if not ids:
        return []
    return [int(i.strip()) for i in ids.split(",")]


def get_encoded_tokens(content: str) -> list[int]:
    return ENCODER.encode(content)


def get_decoded_tokens(tokens: list[int]) -> str:
    return ENCODER.decode(tokens)


def truncate_string(content: str, max_tokens: int) -> str:
    tokens = get_encoded_tokens(content)
    tailing = "" if len(tokens) <= max_tokens else "..."
    return get_decoded_tokens(tokens[:max_tokens]) + tailing


def pack_blob_from_db(blob: GeneralBlob, blob_type: BlobType) -> Blob:
    blob_data = blob.blob_data
    match blob_type:
        case BlobType.chat:
            return ChatBlob(**blob_data, created_at=blob.created_at)
        case BlobType.doc:
            return DocBlob(**blob_data, created_at=blob.created_at)
        case BlobType.summary:
            return SummaryBlob(**blob_data, created_at=blob.created_at)
        case _:
            raise ValueError(f"Unsupported Blob Type: {blob_type}")


def get_message_timestamp(
    message: OpenAICompatibleMessage, fallback_blob_timestamp: datetime
):
    fallback_blob_timestamp = fallback_blob_timestamp or datetime.now()
    fallback_blob_timestamp = fallback_blob_timestamp.astimezone(CONFIG.timezone)
    return (
        message.created_at
        if message.created_at
        else fallback_blob_timestamp.strftime("%Y/%m/%d")
    )


def get_message_name(message: OpenAICompatibleMessage):
    if message.alias:
        # if message.role == "assistant":
        #     return f"{message.alias}"
        return f"{message.alias}({message.role})"
    return message.role


def get_blob_str(blob: Blob):
    match blob.type:
        case BlobType.chat:
            return "\n".join(
                [
                    f"[{get_message_timestamp(m, blob.created_at)}] {get_message_name(m)}: {m.content}"
                    for m in cast(ChatBlob, blob).messages
                ]
            )
        case BlobType.doc:
            return cast(DocBlob, blob).content
        case BlobType.summary:
            time_created = cast(SummaryBlob, blob).created_at or datetime.now()
            clean_summary = cast(SummaryBlob, blob).summary.replace("\n", " ")
            return f"- {clean_summary}[{time_created.strftime("%Y/%m/%d")}]"
        case _:
            raise ValueError(f"Unsupported Blob Type: {blob.type}")


def get_blob_token_size(blob: Blob):
    return len(get_encoded_tokens(get_blob_str(blob)))


def seconds_from_now(dt: datetime):
    return (datetime.now().astimezone() - dt.astimezone()).seconds


def is_valid_profile_config(profile_config: str | None) -> Promise[None]:
    if profile_config is None:
        return Promise.resolve(None)
    # check if the profile config is valid yaml
    try:
        if len(profile_config) > 65535:
            return Promise.reject(CODE.BAD_REQUEST, "Profile config is too long")
        ProfileConfig.load_config_string(profile_config)
        return Promise.resolve(None)
    except yaml.YAMLError as e:
        return Promise.reject(CODE.BAD_REQUEST, f"Invalid profile config: {e}")
    except ValidationError as e:
        return Promise.reject(CODE.BAD_REQUEST, f"Invalid profile config: {e}")
