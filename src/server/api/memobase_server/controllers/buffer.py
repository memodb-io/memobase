from sqlalchemy import func
from pydantic import BaseModel
from ..env import CONFIG, LOG, BufferStatus
from ..utils import (
    get_blob_token_size,
    pack_blob_from_db,
)
from ..models.utils import Promise
from ..models.response import CODE, ChatModalResponse, IdsData
from ..models.database import BufferZone, GeneralBlob
from ..models.blob import BlobType, Blob
from ..connectors import Session
from .modal import BLOBS_PROCESS


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


async def insert_blob_to_buffer(
    user_id: str, project_id: str, blob_id: str, blob_data: Blob
) -> Promise[None]:
    with Session() as session:
        buffer = BufferZone(
            user_id=user_id,
            blob_id=blob_id,
            blob_type=blob_data.type,
            token_size=get_blob_token_size(blob_data),
            project_id=project_id,
            status=BufferStatus.idle,
        )
        session.add(buffer)
        session.commit()
    return Promise.resolve(None)


async def wait_insert_done_then_flush(
    user_id: str, project_id: str, blob_type: BlobType
) -> Promise[ChatModalResponse | None]:
    p = await get_unprocessed_buffer_ids(user_id, project_id, blob_type)
    if not p.ok():
        return p
    if p.data() is None:
        return Promise.resolve([])
    p = await flush_buffer_by_ids(user_id, project_id, blob_type, p.data().ids)
    if not p.ok():
        return p
    if p.data() is not None:
        return Promise.resolve(p.data())
    return Promise.resolve(None)


async def detect_buffer_full_or_not(
    user_id: str, project_id: str, blob_type: BlobType
) -> Promise[IdsData | None]:
    with Session() as session:
        # 1. if buffer size reach maximum, flush it
        buffer_zone = (
            session.query(BufferZone.id, BufferZone.token_size)
            .filter_by(
                user_id=user_id,
                blob_type=str(blob_type),
                project_id=project_id,
                status=BufferStatus.idle,
            )
            .all()
        )
        buffer_ids = [row.id for row in buffer_zone]
        buffer_token_size = sum(row.token_size for row in buffer_zone)
        if (
            buffer_token_size
            and buffer_token_size > CONFIG.max_chat_blob_buffer_token_size
        ):
            LOG.info(
                f"Flush {blob_type} buffer for user {user_id} due to reach maximum token size({buffer_token_size} > {CONFIG.max_chat_blob_buffer_token_size})"
            )

            return Promise.resolve(IdsData(ids=buffer_ids))
    return Promise.resolve(IdsData(ids=[]))


async def get_unprocessed_buffer_ids(
    user_id: str,
    project_id: str,
    blob_type: BlobType,
    select_status: str = BufferStatus.idle,
) -> Promise[IdsData]:
    with Session() as session:
        buffer_ids = (
            session.query(BufferZone.id)
            .filter_by(
                user_id=user_id,
                blob_type=str(blob_type),
                project_id=project_id,
                status=select_status,
            )
            .all()
        )
        return Promise.resolve(IdsData(ids=[row.id for row in buffer_ids]))


async def flush_buffer_by_ids(
    user_id: str,
    project_id: str,
    blob_type: BlobType,
    buffer_ids: list[str],
    select_status: str = BufferStatus.idle,
) -> Promise[ChatModalResponse | None]:
    # FIXME: parallel calling will cause duplicated flush
    if blob_type not in BLOBS_PROCESS:
        return Promise.reject(CODE.BAD_REQUEST, f"Blob type {blob_type} not supported")
    if not len(buffer_ids):
        return Promise.resolve(None)
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
                BufferZone.status == select_status,
                BufferZone.id.in_(buffer_ids),
            )
            .order_by(BufferZone.created_at)
            .all()
        )
        # Update buffer status to processing
        process_buffer_ids = [row.buffer_id for row in buffer_blob_data]
        if select_status != BufferStatus.processing:
            session.query(BufferZone).filter(
                BufferZone.id.in_(process_buffer_ids),
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
                    BufferZone.id.in_(process_buffer_ids),
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


async def flush_buffer(
    user_id: str, project_id: str, blob_type: BlobType
) -> Promise[ChatModalResponse | None]:
    p = await get_unprocessed_buffer_ids(user_id, project_id, blob_type)
    if not p.ok():
        return p
    p = await flush_buffer_by_ids(user_id, project_id, blob_type, p.data().ids)
    return p
