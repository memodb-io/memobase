import pydantic
from ..models.utils import Promise
from ..models.database import GeneralBlob, DEFAULT_PROJECT_ID
from ..models.response import CODE, BlobData, IdData
from ..models.blob import ChatBlob, DocBlob, BlobType
from ..connectors import Session


async def insert_blob(user_id: str, project_id: str, blob: BlobData) -> Promise[IdData]:
    try:
        blob_parsed = blob.to_blob()
    except pydantic.ValidationError as e:
        return Promise.reject(CODE.BAD_REQUEST, f"Unable to parse blob: {e}")
    with Session() as session:
        blob_db = GeneralBlob(
            blob_type=blob_parsed.type,
            blob_data=blob_parsed.get_blob_data(),
            additional_fields=blob_parsed.fields,
            user_id=user_id,
            project_id=project_id,
        )
        session.add(blob_db)
        session.commit()
        b_id = blob_db.id
    return Promise.resolve(IdData(id=b_id))


async def get_blob(user_id: str, project_id: str, blob_id: str) -> Promise[BlobData]:
    with Session() as session:
        blob_db = (
            session.query(GeneralBlob)
            .filter_by(id=blob_id, user_id=user_id, project_id=project_id)
            .one_or_none()
        )
        if not blob_db:
            return Promise.reject(
                CODE.NOT_FOUND, f"Blob with id {blob_id} of user {user_id} not found"
            )
        rt_blob = BlobData(
            blob_type=BlobType(blob_db.blob_type),
            blob_data=blob_db.blob_data,
            fields=blob_db.additional_fields,
            created_at=blob_db.created_at,
            updated_at=blob_db.updated_at,
        )
        return Promise.resolve(rt_blob)


async def remove_blob(user_id: str, project_id: str, blob_id: str) -> Promise[None]:
    with Session() as session:
        blob_db = (
            session.query(GeneralBlob)
            .filter_by(id=blob_id, user_id=user_id, project_id=project_id)
            .one_or_none()
        )
        if not blob_db:
            return Promise.resolve(None)
        else:
            session.delete(blob_db)
            session.commit()
    return Promise.resolve(None)
