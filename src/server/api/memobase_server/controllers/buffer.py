from sqlalchemy import func
from datetime import datetime
from ..env import CONFIG, LOG
from ..utils import (
    get_blob_token_size,
    pack_blob_from_db,
    seconds_from_now,
    user_id_lock,
)
from ..models.utils import Promise
from ..models.response import CODE
from ..models.database import BufferZone, GeneralBlob
from ..models.blob import BlobType, Blob
from ..connectors import Session
from .modal import BLOBS_PROCESS


@user_id_lock("insert_blob_to_buffer")
async def insert_blob_to_buffer(
    user_id: str, blob_id: str, blob_data: Blob
) -> Promise[None]:
    p = await detect_buffer_idle_or_not(user_id, blob_data.type)
    if not p.ok():
        return p

    with Session() as session:
        buffer = BufferZone(
            user_id=user_id,
            blob_id=blob_id,
            blob_type=blob_data.type,
            token_size=get_blob_token_size(blob_data),
        )
        session.add(buffer)
        session.commit()

    p = await detect_buffer_full_or_not(user_id, blob_data.type)
    if not p.ok():
        return p
    return Promise.resolve(None)


# If there're ongoing insert, wait for them to finish then flush
@user_id_lock("insert_blob_to_buffer")
async def wait_insert_done_then_flush(
    user_id: str, blob_type: BlobType
) -> Promise[None]:
    p = await flush_buffer(user_id, blob_type)
    if not p.ok():
        return p
    return Promise.resolve(None)


async def get_buffer_capacity(user_id: str, blob_type: BlobType) -> Promise[int]:
    with Session() as session:
        buffer_count = (
            session.query(BufferZone)
            .filter_by(user_id=user_id, blob_type=str(blob_type))
            .count()
        )
    return Promise.resolve(buffer_count)


async def detect_buffer_full_or_not(user_id: str, blob_type: BlobType) -> Promise[bool]:
    with Session() as session:
        # 1. if buffer size reach maximum, flush it
        buffer_size = (
            session.query(func.sum(BufferZone.token_size))
            .filter_by(user_id=user_id, blob_type=str(blob_type))
            .scalar()
        )
        if buffer_size and buffer_size > CONFIG.max_chat_blob_buffer_token_size:
            LOG.info(
                f"Flush {blob_type} buffer for user {user_id} due to reach maximum token size({buffer_size} > {CONFIG.max_chat_blob_buffer_token_size})"
            )
            p = await flush_buffer(user_id, blob_type)
            if not p.ok():
                return p
            return Promise.resolve(True)
    return Promise.resolve(False)


async def detect_buffer_idle_or_not(user_id: str, blob_type: BlobType) -> Promise[bool]:
    with Session() as session:
        # if buffer is idle for a long time, flush it
        last_buffer_update = (
            session.query(func.max(BufferZone.created_at))
            .filter_by(user_id=user_id, blob_type=str(blob_type))
            .scalar()
        )
        if (
            last_buffer_update
            and seconds_from_now(last_buffer_update) > CONFIG.buffer_flush_interval
        ):
            LOG.info(
                f"Flush {blob_type} buffer for user {user_id} due to idle for a long time"
            )
            p = await flush_buffer(user_id, blob_type)
            if not p.ok():
                return p
            return Promise.resolve(True)
    return Promise.resolve(False)


async def flush_buffer(user_id: str, blob_type: BlobType) -> Promise[None]:
    # FIXME: parallel calling will cause duplicated flush
    with Session() as session:
        # 1. locate all blobs in buffer
        blob_buffers = (
            session.query(BufferZone)
            .filter_by(user_id=user_id, blob_type=str(blob_type))
            .order_by(BufferZone.created_at)
            .all()
        )
        try:
            # 1.1
            total_token_size = sum(b.token_size for b in blob_buffers)
            LOG.info(
                f"Flush {blob_type} buffer for user {user_id} with {len(blob_buffers)} blobs and total token size({total_token_size})"
            )
            if not blob_buffers:
                LOG.info(f"No {blob_type} buffer to flush for user {user_id}")
                return Promise.resolve(None)

            # 2. get all blobs data, convert it to string repr
            blob_ids = [b.blob_id for b in blob_buffers]
            blob_data = (
                session.query(GeneralBlob.created_at, GeneralBlob.blob_data)
                .filter(GeneralBlob.id.in_(blob_ids))
                .all()
            )
            blobs = [pack_blob_from_db(bd, blob_type) for bd in blob_data]
        except Exception as e:
            LOG.error(f"Error in flush_buffer: {e}")
            return Promise.reject(
                CODE.INTERNAL_SERVER_ERROR, f"Error in flush_buffer: {e}"
            )
        finally:
            # FIXME: when failed, the buffer will be deleted anyway. Add some rollback maybe
            for buffer in blob_buffers:
                session.delete(buffer)
            session.commit()
    p = await BLOBS_PROCESS[blob_type](user_id, blob_ids, blobs)
    if not p.ok():
        return p
    LOG.info(f"Flush {blob_type} buffer(size: {len(blob_buffers)}) for user {user_id}")
    return Promise.resolve(None)
