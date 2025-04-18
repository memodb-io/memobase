import yaml
from typing import cast
from datetime import timezone, datetime
from functools import wraps
from pydantic import ValidationError
from .env import ENCODER, LOG, CONFIG, ProfileConfig
from .models.blob import Blob, BlobType, ChatBlob, DocBlob, OpenAICompatibleMessage
from .models.database import GeneralBlob
from .models.response import UserEventData
from .models.utils import Promise, CODE
from .connectors import get_redis_client, PROJECT_ID


def event_str_repr(event: UserEventData) -> str:
    happened_at = event.created_at.astimezone(CONFIG.timezone).strftime("%Y/%m/%d")
    event_data = event.event_data
    if event_data.event_tip is None:
        profile_deltas = [
            f"- {ed.attributes['topic']}::{ed.attributes['sub_topic']}: {ed.content}"
            for ed in event_data.profile_delta
        ]
        profile_delta_str = "\n".join(profile_deltas)
        return f"{happened_at}:\n{profile_delta_str}"
    else:
        if event_data.event_tags:
            event_tags = "\n".join(
                [f"- {tag.tag}: {tag.value}" for tag in event_data.event_tags]
            )
        else:
            event_tags = ""
        return f"{happened_at}:\n{event_data.event_tip}\n{event_tags}"


def get_encoded_tokens(content: str) -> list[int]:
    return ENCODER.encode(content)


def get_decoded_tokens(tokens: list[int]) -> str:
    return ENCODER.decode(tokens)


def truncate_string(content: str, max_tokens: int):
    return get_decoded_tokens(get_encoded_tokens(content)[:max_tokens])


def pack_blob_from_db(blob: GeneralBlob, blob_type: BlobType) -> Blob:
    blob_data = blob.blob_data
    match blob_type:
        case BlobType.chat:
            return ChatBlob(**blob_data, created_at=blob.created_at)
        case BlobType.doc:
            return DocBlob(**blob_data, created_at=blob.created_at)
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
        case _:
            raise ValueError(f"Unsupported Blob Type: {blob.type}")


def get_blob_token_size(blob: Blob):
    return len(get_encoded_tokens(get_blob_str(blob)))


def seconds_from_now(dt: datetime):
    return (datetime.now().astimezone() - dt.astimezone()).seconds


def user_id_lock(scope, lock_timeout=128, blocking_timeout=32):
    def __user_id_lock(func):
        @wraps(func)
        async def wrapper(user_id, *args, **kwargs):
            lock_key = f"user_lock:{PROJECT_ID}:{scope}:{user_id}"
            async with get_redis_client() as redis_client:
                lock = redis_client.lock(
                    lock_key, timeout=lock_timeout, blocking_timeout=blocking_timeout
                )
                try:
                    if not await lock.acquire(blocking=True):
                        raise TimeoutError(
                            f"Could not acquire lock for user {user_id} in scope {scope}"
                        )
                    return await func(user_id, *args, **kwargs)
                finally:
                    try:
                        if await lock.locked():
                            await lock.release()
                    except Exception as e:
                        LOG.error(
                            f"Error releasing lock for user {user_id} in scope {scope}: {e}"
                        )
                        # Consider forcing lock release or implementing a recovery mechanism
                        # raise RuntimeError(f"Lock release failed: {e}") from e

        return wrapper

    return __user_id_lock


def is_valid_profile_config(profile_config: str | None) -> Promise[None]:
    if profile_config is None:
        return Promise.resolve(None)
    # check if the profile config is valid yaml
    try:
        if len(profile_config) > 65535:
            return False
        ProfileConfig.load_config_string(profile_config)
        return Promise.resolve(None)
    except yaml.YAMLError as e:
        return Promise.reject(CODE.BAD_REQUEST, f"Invalid profile config: {e}")
    except ValidationError as e:
        return Promise.reject(CODE.BAD_REQUEST, f"Invalid profile config: {e}")
