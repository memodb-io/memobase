from sqlalchemy import func
from ..env import CONFIG, LOG
from ..utils import get_blob_token_size, pack_blob_from_db, get_blob_str
from ..models.utils import Promise
from ..models.database import BufferZone, GeneralBlob
from ..models.response import CODE, BlobData, IdData
from ..models.blob import ChatBlob, DocBlob, BlobType, Blob
from ..connectors import Session


async def flush_reach_maximum_token_buffer(
    user_id: str, blob_type: BlobType
) -> Promise[bool]:
    with Session() as session:
        buffer_size = (
            session.query(func.sum(BufferZone.token_size))
            .filter_by(user_id=user_id, blob_type=str(blob_type))
            .scalar()
        )
        if buffer_size and buffer_size > CONFIG.max_chat_blob_buffer_token_size:
            LOG.info(
                f"Flush {blob_type} buffer for user {user_id} due to reach maximum token size"
            )
            await flush_buffer(user_id, blob_type)
            return Promise.resolve(True)
    return Promise.resolve(False)


async def insert_blob_to_buffer(
    user_id: str, blob_id: str, blob_data: Blob
) -> Promise[None]:
    p = await flush_reach_maximum_token_buffer(user_id, blob_data.type)
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
    return Promise.resolve(None)


async def flush_buffer(user_id: str, blob_type: BlobType) -> Promise[None]:
    with Session() as session:
        # 1. locate all blobs in buffer
        blob_buffers = (
            session.query(BufferZone)
            .filter_by(user_id=user_id, blob_type=str(blob_type))
            .all()
        )
        # 1.1
        if not blob_buffers:
            LOG.info(f"No {blob_type} buffer to flush for user {user_id}")
            return Promise.resolve(None)

        # 2. get all blobs data, convert it to string repr
        blob_ids = [b.blob_id for b in blob_buffers]
        blob_data = (
            session.query(GeneralBlob.blob_data)
            .filter(GeneralBlob.id.in_(blob_ids))
            .all()
        )
        blobs = [pack_blob_from_db(bd.blob_data, blob_type) for bd in blob_data]
        blob_strs = [get_blob_str(bd) for bd in blobs]
        # 3. process blobs reprs with memory

        for buffer in blob_buffers:
            session.delete(buffer)
        LOG.info(
            f"Flush {blob_type} buffer(size: {len(blob_buffers)}) for user {user_id}"
        )
        session.commit()
