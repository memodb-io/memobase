from ..models.database import Project
from ..models.utils import Promise, CODE
from ..models.response import IdData
from ..connectors import Session


async def create_project(
    project_id: str, project_secret: str, profile_config: str = None
) -> Promise[IdData]:
    with Session() as session:
        proj = Project(
            project_id=project_id,
            project_secret=project_secret,
            profile_config=profile_config,
        )
        session.add(proj)
        session.commit()
        pid = proj.id
    return Promise.resolve(IdData(id=pid))


async def delete_project(project_id: str) -> Promise[None]:
    with Session() as session:
        p = (
            session.query(Project)
            .filter(Project.project_id == project_id)
            .one_or_none()
        )
        if not p:
            return Promise.reject(CODE.NOT_FOUND, "Project not found")
        session.delete(p)
        session.commit()
    return Promise.resolve(None)


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


async def update_project_secret(project_id: str, project_secret: str) -> Promise[None]:
    with Session() as session:
        p = (
            session.query(Project)
            .filter(Project.project_id == project_id)
            .one_or_none()
        )
        if not p:
            return Promise.reject(CODE.NOT_FOUND, "Project not found")
        p.project_secret = project_secret
        session.commit()
    return Promise.resolve(None)
