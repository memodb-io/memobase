from fastapi import BackgroundTasks, Request
from fastapi import Path, Body, Query
import traceback

from ..controllers import full as controllers

from ..env import TelemetryKeyName, TRACE_LOG
from ..models.response import CODE, UUID
from ..models.utils import Promise
from ..models import response as res
from ..telemetry.capture_key import capture_int_key


async def insert_blob(
    request: Request,
    user_id: UUID = Path(..., description="The ID of the user to insert the blob for"),
    wait_process: bool = Query(
        False, description="Whether to wait for the blob to be processed"
    ),
    blob_data: res.BlobData = Body(..., description="The blob data to insert"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
) -> res.BlobInsertResponse:
    project_id = request.state.memobase_project_id
    background_tasks.add_task(
        capture_int_key, TelemetryKeyName.insert_blob_request, project_id=project_id
    )

    p = await controllers.billing.get_project_billing(project_id)
    if not p.ok():
        return p.to_response(res.IdResponse)
    billing = p.data()

    if billing.token_left is not None and billing.token_left < 0:
        return Promise.reject(
            CODE.SERVICE_UNAVAILABLE,
            f"Your project reaches Memobase token limit, "
            f"Left: {billing.token_left}, this project used: {billing.project_token_cost_month}. "
            f"Your quota will be refilled on {billing.next_refill_at}. "
            "\nhttps://www.memobase.io/pricing for more information.",
        ).to_response(res.IdResponse)

    try:
        insert_result = await controllers.blob.insert_blob(
            user_id, project_id, blob_data
        )
        if not insert_result.ok():
            return insert_result.to_response(res.BaseResponse)
        bid = insert_result.data().id

        pb = await controllers.buffer.insert_blob_to_buffer(
            user_id, project_id, bid, blob_data.to_blob()
        )
        if not pb.ok():
            return pb.to_response(res.BaseResponse)

        process_ids = await controllers.buffer.detect_buffer_full_or_not(
            user_id, project_id, blob_data.blob_type
        )
        if not process_ids.ok():
            return process_ids.to_response(res.BaseResponse)

        final_results = []
        # need to process buffer
        if process_ids.data() is not None and len(process_ids.data().ids):
            if wait_process:
                # sync
                p = await controllers.buffer.flush_buffer_by_ids(
                    user_id, project_id, blob_data.blob_type, process_ids.data().ids
                )
                if not p.ok():
                    return p.to_response(res.BaseResponse)
                if p.data() is not None:
                    final_results.append(p.data())
            else:
                # async
                background_tasks.add_task(
                    controllers.buffer_background.flush_buffer_by_ids_in_background,
                    user_id,
                    project_id,
                    blob_data.blob_type,
                    process_ids.data().ids,
                )
    except Exception as e:
        TRACE_LOG.error(
            project_id, user_id, f"Error inserting blob: {e}, {traceback.format_exc()}"
        )
        return Promise.reject(
            CODE.INTERNAL_SERVER_ERROR, f"Error inserting blob: {e}"
        ).to_response(res.BaseResponse)

    background_tasks.add_task(
        capture_int_key,
        TelemetryKeyName.insert_blob_success_request,
        project_id=project_id,
    )
    return res.BlobInsertResponse(
        data={**insert_result.data().model_dump(), "chat_results": final_results}
    )


async def get_blob(
    request: Request,
    user_id: UUID = Path(..., description="The ID of the user"),
    blob_id: UUID = Path(..., description="The ID of the blob to retrieve"),
) -> res.BlobDataResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.blob.get_blob(user_id, project_id, blob_id)
    return p.to_response(res.BlobDataResponse)


async def delete_blob(
    request: Request,
    user_id: UUID = Path(..., description="The ID of the user"),
    blob_id: UUID = Path(..., description="The ID of the blob to delete"),
) -> res.BaseResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.blob.remove_blob(user_id, project_id, blob_id)
    return p.to_response(res.BaseResponse)
