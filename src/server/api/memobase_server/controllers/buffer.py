from sqlalchemy import func
from ..env import CONFIG, LOG
from ..utils import get_blob_token_size
from ..models.utils import Promise
from ..models.database import BufferZone
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
    print("FLUSH")
