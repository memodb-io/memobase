from typing import cast
from datetime import timezone, datetime
from functools import wraps
from .env import ENCODER, LOG
from .models.blob import Blob, BlobType, ChatBlob, DocBlob
from .connectors import get_redis_client


def get_encoded_tokens(content: str):
    return ENCODER.encode(content)


def get_decoded_tokens(tokens: list[int]):
    return ENCODER.decode(tokens)


def pack_blob_from_db(blob_data: dict, blob_type: BlobType) -> Blob:
    match blob_type:
        case BlobType.chat:
            return ChatBlob(**blob_data)
        case BlobType.doc:
            return DocBlob(**blob_data)
        case _:
            raise ValueError(f"Unsupported Blob Type: {blob_type}")


def get_blob_str(blob: Blob):
    match blob.type:
        case BlobType.chat:
            return "\n".join(
                [
                    f"{m.alias or m.role}: {m.content}"
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


def user_id_lock(func):
    @wraps(func)
    async def wrapper(user_id, *args, **kwargs):
        redis_client = get_redis_client()
        lock_key = f"user_lock:{user_id}"
        lock = redis_client.lock(lock_key, timeout=60)  # 30 seconds timeout
        print("ENTERING LOCK", user_id)
        try:
            if not lock.acquire(blocking=True):  # 5 seconds wait
                print("TIMEOUT!!!!!")
                raise TimeoutError("Could not acquire lock")
            return await func(user_id, *args, **kwargs)
        finally:
            try:
                lock.release()
                print("RELEASED LOCK", user_id)
            except Exception as e:
                print(f"Error releasing lock: {e}")

    return wrapper
