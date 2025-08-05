from httpx import AsyncClient
import uuid

from ..models.response import BillingData, BaseResponse
from ..models.utils import Promise, CODE
from ..connectors import ADMIN_URL, ADMIN_TOKEN


async def get_project_usage(project_id: str) -> Promise[BillingData]:
    if ADMIN_URL is None:
        return Promise.reject(CODE.SERVICE_UNAVAILABLE, "Memobase Admin URL not set")
    async with AsyncClient(
        base_url=ADMIN_URL, headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
    ) as client:
        request_id = str(uuid.uuid4())
        response = await client.get(
            f"/api/v1/billing/project/{project_id}",
            timeout=10,
            headers={"X-Request-ID": request_id},
        )

        if response.status_code != 200:
            return Promise.reject(
                CODE.SERVICE_UNAVAILABLE,
                f"Failed to get project usage: {response.text}",
            )
        data = response.json()
        if data["errno"] != 0:
            return Promise.reject(
                CODE.SERVICE_UNAVAILABLE,
                f"Failed to get project usage: {data}",
            )
        return Promise.resolve(BillingData(**data["data"]))


async def cost_project_usage(
    project_id: str, input_tokens: int, output_tokens: int
) -> Promise[None]:
    if ADMIN_URL is None:
        return Promise.reject(CODE.SERVICE_UNAVAILABLE, "Memobase Admin URL not set")
    async with AsyncClient(
        base_url=ADMIN_URL, headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
    ) as client:
        request_id = str(uuid.uuid4())
        response = await client.put(
            f"/api/v1/billing/project/{project_id}",
            json={"usage": input_tokens + output_tokens},
            headers={"X-Request-ID": request_id},
        )
        if response.status_code != 200:
            return Promise.reject(
                CODE.SERVICE_UNAVAILABLE,
                f"Failed to cost project usage: {response.text}",
            )
        data = response.json()
        if data["errno"] != 0:
            return Promise.reject(
                CODE.SERVICE_UNAVAILABLE,
                f"Failed to cost project usage: {data}",
            )
        return Promise.resolve(None)
