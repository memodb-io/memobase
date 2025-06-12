import uuid
import asyncio
import traceback
from sqlalchemy import func
from pydantic import BaseModel
from ..env import CONFIG, LOG, BufferStatus
from ..models.utils import Promise
from ..models.response import CODE, ChatModalResponse, IdsData, UUID
from ..models.database import BufferZone, GeneralBlob
from ..models.blob import BlobType, Blob
from ..connectors import Session, PROJECT_ID, get_redis_client
from .modal import BLOBS_PROCESS
from .buffer import flush_buffer_by_ids

REDIS_LUA_CHECK_AND_DELETE_LOCK = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
"""


def get_user_lock_key(user_id: str, project_id: str, scope: str) -> str:
    return f"memobase:user_lock:{PROJECT_ID}:{scope}:{project_id}:{user_id}"


def get_user_buffer_queue_key(user_id: str, project_id: str, scope: str) -> str:
    return f"memobase:user_buffer_queue:{PROJECT_ID}:{scope}:{project_id}:{user_id}"


def pack_ids_to_str(ids: list[str]) -> str:
    return "::".join([str(i) for i in ids])


def unpack_ids_from_str(ids_str: str) -> list[str]:
    return [i.strip() for i in ids_str.split("::") if i.strip()]


async def flush_buffer_by_ids_in_background(
    user_id: str, project_id: str, blob_type: BlobType, buffer_ids: list[str]
) -> None:
    if not len(buffer_ids):
        return
    if blob_type not in BLOBS_PROCESS:
        return

    # 1. mark buffer as processing
    with Session() as session:
        buffer_blob_data = (
            session.query(BufferZone.id)
            .filter(
                BufferZone.user_id == user_id,
                BufferZone.blob_type == str(blob_type),
                BufferZone.project_id == project_id,
                BufferZone.status == BufferStatus.idle,
                BufferZone.id.in_(buffer_ids),
            )
            .order_by(BufferZone.created_at)
            .all()
        )
        actual_buffer_ids = [row.id for row in buffer_blob_data]
        if not len(actual_buffer_ids):
            return
        session.query(BufferZone).filter(
            BufferZone.id.in_(actual_buffer_ids),
        ).update(
            {BufferZone.status: BufferStatus.processing},
            synchronize_session=False,
        )

        session.commit()

    # 2. add actual buffer ids to a redis queue
    buffer_queue_key = get_user_buffer_queue_key(
        user_id, project_id, f"flush_buffer_background_{blob_type}"
    )
    buffer_ids_str = pack_ids_to_str(actual_buffer_ids)

    try:
        async with get_redis_client() as redis_client:
            await redis_client.rpush(buffer_queue_key, buffer_ids_str)

            queue_size = await redis_client.llen(buffer_queue_key)

            LOG.info(
                f"[background] Enqueued {len(actual_buffer_ids)} buffer IDs for user {user_id} to queue (queue size: {queue_size})"
            )

        await flush_buffer_background_running(user_id, project_id, blob_type)
    except Exception as e:
        LOG.error(
            f"[background] Error enqueue buffer ids: {e}: {traceback.format_exc()}"
        )


async def flush_buffer_background_running(
    user_id: str,
    project_id: str,
    blob_type: BlobType,
    asleep_waiting_s: float = 0.001,
    max_iterations: int = 1000,
    process_interval_s: float = 60 * 10,
):
    user_key = get_user_lock_key(
        user_id, project_id, f"flush_buffer_background_{blob_type}"
    )
    buffer_queue_key = get_user_buffer_queue_key(
        user_id, project_id, f"flush_buffer_background_{blob_type}"
    )

    __lock_value = str(uuid.uuid4())

    # Shorter lock timeout with renewal
    async with get_redis_client() as redis_client:
        acquired = await redis_client.set(
            user_key, __lock_value, nx=True, ex=process_interval_s
        )  # 5 minutes
        if not acquired:
            return

    try:
        iteration_count = 0
        while iteration_count < max_iterations:
            async with get_redis_client() as redis_client:
                lock_value = await redis_client.get(user_key)
                if lock_value is None or lock_value != __lock_value:  # Lock is expired
                    break

                buffer_ids_str = await redis_client.lpop(buffer_queue_key)
                if buffer_ids_str is None:  # Queue is empty
                    break

                # Renew lock timeout if needed
                await redis_client.expire(user_key, process_interval_s)
                current_queue_size = await redis_client.llen(buffer_queue_key)
            LOG.info(
                f"[background]({iteration_count}/{max_iterations}) Processing buffer for user {user_id} (left queue size: {current_queue_size})"
            )
            buffer_ids = unpack_ids_from_str(buffer_ids_str or "")
            if not buffer_ids:
                continue

            try:
                p = await flush_buffer_by_ids(
                    user_id,
                    project_id,
                    blob_type,
                    buffer_ids,
                    select_status=BufferStatus.processing,
                )
                if not p.ok():
                    LOG.error(f"[background] Error flushing buffer by ids: {p.msg()}")
                    # TODO: Add to dead letter queue or retry mechanism
            except Exception as e:
                LOG.error(
                    f"[background] Unknown Error flushing buffer by ids: {e}\n{traceback.format_exc()}"
                )
                # TODO: Add to dead letter queue

            await asyncio.sleep(asleep_waiting_s)
            iteration_count += 1

    finally:
        try:
            async with get_redis_client() as redis_client:
                await redis_client.eval(
                    REDIS_LUA_CHECK_AND_DELETE_LOCK, 1, user_key, lock_value
                )
        except Exception as e:
            LOG.error(f"[background] Failed to release lock for user {user_id}: {e}")
