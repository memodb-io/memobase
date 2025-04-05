from ..models.database import Project
from ..models.utils import Promise, CODE
from ..models.response import IdData, ProfileConfigData
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
        if not p.profile_config:
            return Promise.resolve(ProfileConfig())
        p_parse = ProfileConfig.load_config_string(p.profile_config)
    return Promise.resolve(p_parse)


async def update_project_profile_config(
    project_id: str, profile_config: str | None
) -> Promise[None]:
    with Session() as session:
        p = (
            session.query(Project)
            .filter(Project.project_id == project_id)
            .one_or_none()
        )
        if not p:
            return Promise.reject(CODE.NOT_FOUND, "Project not found")
        p.profile_config = profile_config
        session.commit()
    return Promise.resolve(None)


async def get_project_profile_config_string(
    project_id: str,
) -> Promise[ProfileConfigData]:
    with Session() as session:
        p = (
            session.query(Project.profile_config)
            .filter(Project.project_id == project_id)
            .one_or_none()
        )
        if not p:
            return Promise.reject(CODE.NOT_FOUND, "Project not found")
        return Promise.resolve(ProfileConfigData(profile_config=p.profile_config or ""))
