import traceback
from fastapi import HTTPException, Request
from ..env import LOG
from ..models.response import BaseResponse, CODE
from ..models.database import DEFAULT_PROJECT_ID
from ..connectors import db_health_check, redis_health_check
from ..llms.embeddings import check_embedding_sanity
from ..llms import llm_sanity_check


async def healthcheck() -> BaseResponse:
    """Check if your memobase is set up correctly"""
    LOG.info("Healthcheck requested")
    if not db_health_check():
        raise HTTPException(
            status_code=CODE.INTERNAL_SERVER_ERROR.value,
            detail="Database not available",
        )
    if not await redis_health_check():
        raise HTTPException(
            status_code=CODE.INTERNAL_SERVER_ERROR.value,
            detail="Redis not available",
        )
    return BaseResponse()


async def root_running_status_check(request: Request) -> BaseResponse:
    """Check if your memobase is set up correctly"""
    project_id = request.state.memobase_project_id
    if project_id != DEFAULT_PROJECT_ID:
        return BaseResponse(
            errno=CODE.METHOD_NOT_ALLOWED, errmsg="Only Root can access this"
        )
    try:
        if not db_health_check():
            return BaseResponse(
                errno=CODE.INTERNAL_SERVER_ERROR,
                errmsg="Database not available",
            )
        if not await redis_health_check():
            return BaseResponse(
                errno=CODE.INTERNAL_SERVER_ERROR,
                errmsg="Redis not available",
            )
        await check_embedding_sanity()
        await llm_sanity_check()
    except Exception as e:
        return BaseResponse(
            errno=CODE.INTERNAL_SERVER_ERROR,
            errmsg=f"Occuring Error when status checking: {e}\n{traceback.format_exc()}",
        )

    return BaseResponse()
