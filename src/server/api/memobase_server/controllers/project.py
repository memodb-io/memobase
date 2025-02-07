from ..models.database import Project
from ..models.utils import Promise, CODE
from ..models.response import IdData
from ..connectors import Session
from ..env import ProfileConfig


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


async def get_project_status(project_id: str) -> Promise[str]:
    with Session() as session:
        p = (
            session.query(Project.status)
            .filter(Project.project_id == project_id)
            .one_or_none()
        )
        if not p:
            return Promise.reject(CODE.NOT_FOUND, "Project not found")
        return Promise.resolve(p.status)


async def get_project_profile_config(project_id: str) -> Promise[ProfileConfig]:
    with Session() as session:
        p = (
            session.query(Project.profile_config)
            .filter(Project.project_id == project_id)
            .one_or_none()
        )
        if not p:
            return Promise.reject(CODE.NOT_FOUND, "Project not found")
        if p.profile_config is None:
            return Promise.resolve(ProfileConfig())
        p_parse = ProfileConfig.load_config_string(p.profile_config)
    return Promise.resolve(p_parse)
