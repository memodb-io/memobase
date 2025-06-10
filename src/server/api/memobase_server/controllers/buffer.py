from sqlalchemy import func
from pydantic import BaseModel
from ..env import CONFIG, LOG, BufferStatus
from ..utils import (
    get_blob_token_size,
    pack_blob_from_db,
    seconds_from_now,
)
from ..models.utils import Promise
from ..models.response import CODE, ChatModalResponse
from ..models.database import BufferZone, GeneralBlob
from ..models.blob import BlobType, Blob
from ..connectors import Session
from .modal import BLOBS_PROCESS


async def insert_blob_to_buffer(
    user_id: str, project_id: str, blob_id: str, blob_data: Blob
) -> Promise[list[ChatModalResponse]]:
    results = []
    p = await detect_buffer_idle_or_not(user_id, project_id, blob_data.type)
    if not p.ok():
        return p
    if p.data() is not None:
        results.append(p.data())
    with Session() as session:
        buffer = BufferZone(
            user_id=user_id,
            blob_id=blob_id,
            blob_type=blob_data.type,
            token_size=get_blob_token_size(blob_data),
            project_id=project_id,
        )
        session.add(buffer)
        session.commit()

    p = await detect_buffer_full_or_not(user_id, project_id, blob_data.type)
    if not p.ok():
        return p
    if p.data() is not None:
        results.append(p.data())
    return Promise.resolve(results)


async def wait_insert_done_then_flush(
    user_id: str, project_id: str, blob_type: BlobType
) -> Promise[list[ChatModalResponse]]:
    p = await flush_buffer(user_id, project_id, blob_type)
    if not p.ok():
        return p
    if p.data() is not None:
        return Promise.resolve([p.data()])
    return Promise.resolve([])


async def get_buffer_capacity(
    user_id: str, project_id: str, blob_type: BlobType
) -> Promise[int]:
    with Session() as session:
        buffer_count = (
            session.query(BufferZone.id)
            .filter_by(
                user_id=user_id,
                blob_type=str(blob_type),
                project_id=project_id,
                status=BufferStatus.idle,
            )
            .count()
        )
    return Promise.resolve(buffer_count)


async def detect_buffer_full_or_not(
    user_id: str, project_id: str, blob_type: BlobType
) -> Promise[ChatModalResponse | None]:
    with Session() as session:
        # 1. if buffer size reach maximum, flush it
        buffer_size = (
            session.query(func.sum(BufferZone.token_size))
            .filter_by(user_id=user_id, blob_type=str(blob_type), project_id=project_id)
            .scalar()
        )
        if buffer_size and buffer_size > CONFIG.max_chat_blob_buffer_token_size:
            LOG.info(
                f"Flush {blob_type} buffer for user {user_id} due to reach maximum token size({buffer_size} > {CONFIG.max_chat_blob_buffer_token_size})"
            )
            p = await flush_buffer(user_id, project_id, blob_type)
            return p
    return Promise.resolve(None)


async def detect_buffer_idle_or_not(
    user_id: str, project_id: str, blob_type: BlobType
) -> Promise[ChatModalResponse | None]:
    with Session() as session:
        # if buffer is idle for a long time, flush it
        last_buffer_update = (
            session.query(func.max(BufferZone.created_at))
            .filter_by(user_id=user_id, blob_type=str(blob_type), project_id=project_id)
            .scalar()
        )
        if (
            last_buffer_update
            and seconds_from_now(last_buffer_update) > CONFIG.buffer_flush_interval
        ):
            LOG.info(
                f"Flush {blob_type} buffer for user {user_id} due to idle for a long time"
            )
            p = await flush_buffer(user_id, project_id, blob_type)
            return p
    return Promise.resolve(None)


async def flush_buffer(
    user_id: str, project_id: str, blob_type: BlobType
) -> Promise[ChatModalResponse]:
    # FIXME: parallel calling will cause duplicated flush
    if blob_type not in BLOBS_PROCESS:
        return Promise.reject(CODE.BAD_REQUEST, f"Blob type {blob_type} not supported")

    with Session() as session:
        # Join BufferZone with GeneralBlob to get all data in one query
        buffer_blob_data = (
            session.query(
                BufferZone.id.label("buffer_id"),
                BufferZone.blob_id,
                BufferZone.token_size,
                BufferZone.created_at.label("buffer_created_at"),
                GeneralBlob.created_at,
                GeneralBlob.blob_data,
            )
            .join(GeneralBlob, BufferZone.blob_id == GeneralBlob.id)
            .filter(
                BufferZone.user_id == user_id,
                BufferZone.blob_type == str(blob_type),
                BufferZone.project_id == project_id,
                GeneralBlob.user_id == user_id,
                GeneralBlob.project_id == project_id,
                BufferZone.status == BufferStatus.idle,
            )
            .order_by(BufferZone.created_at)
            .all()
        )
        # Update buffer status to processing
        session.query(BufferZone).filter(
            BufferZone.id.in_([row.buffer_id for row in buffer_blob_data]),
        ).update(
            {BufferZone.status: BufferStatus.processing},
            synchronize_session=False,
        )

        if not buffer_blob_data:
            LOG.info(f"No {blob_type} buffer to flush for user {user_id}")
            return Promise.resolve(None)

        blob_ids = [row.blob_id for row in buffer_blob_data]
        blobs = [pack_blob_from_db(row, blob_type) for row in buffer_blob_data]
        total_token_size = sum(row.token_size for row in buffer_blob_data)
        LOG.info(
            f"Flush {blob_type} buffer for user {user_id} with {len(buffer_blob_data)} blobs and total token size({total_token_size})"
        )

        session.commit()

    try:
        # Pack blobs from the joined data

        # Process blobs first (moved outside the session)
        p = await BLOBS_PROCESS[blob_type](user_id, project_id, blobs)
        if not p.ok():
            return p
        with Session() as session:
            try:
                # Update buffer status to done
                session.query(BufferZone).filter(
                    BufferZone.id.in_([row.buffer_id for row in buffer_blob_data]),
                ).update(
                    {BufferZone.status: BufferStatus.done},
                    synchronize_session=False,
                )
                if blob_type == BlobType.chat and not CONFIG.persistent_chat_blobs:
                    session.query(GeneralBlob).filter(
                        GeneralBlob.id.in_(blob_ids),
                        GeneralBlob.project_id == project_id,
                    ).delete(synchronize_session=False)
                session.commit()
                LOG.info(
                    f"Flushed {blob_type} buffer(size: {len(buffer_blob_data)}) for user {user_id}"
                )
            except Exception as e:
                session.rollback()
                LOG.error(f"DB Error while deleting buffers/blobs: {e}")
                raise e

        return p

    except Exception as e:
        with Session() as session:
            session.query(BufferZone).filter(
                BufferZone.id.in_([row.buffer_id for row in buffer_blob_data]),
            ).update(
                {BufferZone.status: BufferStatus.failed},
                synchronize_session=False,
            )
            session.commit()
        LOG.error(f"Error in flush_buffer: {e}. Buffer status updated to failed.")
        raise e
