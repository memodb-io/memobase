from ..models.database import Project
from ..models.utils import Promise, CODE
from ..models.response import IdData
from ..connectors import Session


async def get_project_secret(project_id: str) -> Promise[str]:
    with Session() as session:
        p = (
            session.query(Project)
            .filter(Project.project_id == project_id)
            .one_or_none()
        )
        if not p:
            return Promise.reject(CODE.NOT_FOUND, "Project not found")
        return Promise.resolve(p.project_secret)
