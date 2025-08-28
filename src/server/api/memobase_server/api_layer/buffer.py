from ..controllers import full as controllers
from ..models.response import UUID, IdsResponse
from ..models.blob import BlobType
from ..models import response as res
from typing import Literal
from fastapi import Request, Query, BackgroundTasks
from fastapi import Path


async def flush_buffer(
    request: Request,
    user_id: UUID = Path(..., description="The ID of the user"),
    buffer_type: BlobType = Path(..., description="The type of buffer to flush"),
    wait_process: bool = Query(
        False, description="Whether to wait for the buffer to be processed"
    ),
    background_tasks: BackgroundTasks = BackgroundTasks(),
) -> res.ChatModalAPIResponse:
    """Flush unprocessed blobs into Memory"""
    project_id = request.state.memobase_project_id
    # p = await controllers.buffer.wait_insert_done_then_flush(
    #     user_id, project_id, buffer_type
    # )

    p = await controllers.buffer.get_unprocessed_buffer_ids(
        user_id, project_id, buffer_type
    )
    if not p.ok():
        return p.to_response(res.BaseResponse)
    if not len(p.data().ids):
        return res.ChatModalAPIResponse(data=[])
    if wait_process:
        p = await controllers.buffer.flush_buffer_by_ids(
            user_id, project_id, buffer_type, p.data().ids
        )
        if not p.ok():
            return p.to_response(res.BaseResponse)
        if p.data() is not None:
            return res.ChatModalAPIResponse(data=[p.data()])
    else:
        background_tasks.add_task(
            controllers.buffer_background.flush_buffer_by_ids_in_background,
            user_id,
            project_id,
            buffer_type,
            p.data().ids,
        )
        return res.ChatModalAPIResponse(data=None)


async def get_processing_buffer_ids(
    request: Request,
    user_id: UUID = Path(..., description="The ID of the user"),
    buffer_type: BlobType = Path(..., description="The type of buffer to flush"),
    status: Literal["idle", "processing", "failed", "done"] = Query(
        "processing", description="The status of the buffer to get"
    ),
) -> IdsResponse:
    """Get processing buffer ids"""
    project_id = request.state.memobase_project_id
    p = await controllers.buffer.get_unprocessed_buffer_ids(
        user_id, project_id, buffer_type, select_status=status
    )
    return p.to_response(IdsResponse)
