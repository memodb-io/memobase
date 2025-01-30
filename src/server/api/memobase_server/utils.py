import yaml
from typing import cast
from datetime import timezone, datetime
from functools import wraps
from .env import ENCODER, LOG
from .models.blob import Blob, BlobType, ChatBlob, DocBlob, OpenAICompatibleMessage
from .models.database import GeneralBlob
from .connectors import get_redis_client, PROJECT_ID


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
    return (
        message.created_at
        if message.created_at
        else fallback_blob_timestamp.strftime("%Y/%m/%d %I:%M%p")
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
    return (datetime.now(tz=timezone.utc) - dt.replace(tzinfo=timezone.utc)).seconds


def user_id_lock(scope):
    def __user_id_lock(func):
        @wraps(func)
        async def wrapper(user_id, *args, **kwargs):
            redis_client = get_redis_client()
            lock_key = f"user_lock:{PROJECT_ID}:{scope}:{user_id}"
            lock = redis_client.lock(lock_key, timeout=30)
            try:
                if not await lock.acquire(
                    blocking=True, blocking_timeout=60
                ):  # 30 seconds wait
                    raise TimeoutError("Could not acquire lock")
                return await func(user_id, *args, **kwargs)
            finally:
                try:
                    await lock.release()
                except Exception as e:
                    LOG.error(f"Error releasing lock: {e}")
                await redis_client.aclose()

        return wrapper

    return __user_id_lock


def is_valid_profile_config(profile_config: str) -> bool:
    # check if the profile config is valid yaml
    try:
        r = yaml.safe_load(profile_config)
        return True
    except yaml.YAMLError as e:
        LOG.error(f"Invalid profile config: {e}")
        return False
