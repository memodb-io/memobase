import json
import time
import memobase_server.env

# Done setting up env

import os
import asyncio
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks, Request
from fastapi import Path, Query, Body
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from starlette.middleware.base import BaseHTTPMiddleware
from memobase_server.connectors import (
    db_health_check,
    redis_health_check,
    close_connection,
    init_redis_pool,
)
from memobase_server import utils
from memobase_server.models.database import DEFAULT_PROJECT_ID
from memobase_server.models.response import BaseResponse, CODE
from memobase_server.models.blob import BlobType
from memobase_server.models.utils import Promise
from memobase_server.models import response as res
from memobase_server import controllers
from memobase_server.telemetry import (
    telemetry_manager,
    CounterMetricName,
    HistogramMetricName,
)
from memobase_server.env import (
    LOG,
    TelemetryKeyName,
    ProjectStatus,
)
from memobase_server.telemetry.capture_key import capture_int_key
from uvicorn.config import LOGGING_CONFIG
from memobase_server.auth.token import (
    parse_project_id,
    check_project_secret,
    get_project_status,
)
from memobase_server import utils


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_redis_pool()
    LOG.info(f"Start Memobase Server {memobase_server.__version__} 🖼️")
    yield
    await close_connection()


app = FastAPI(
    lifespan=lifespan,
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Memobase API",
        version=memobase_server.__version__,
        summary="APIs for Memobase, a user memory system for LLM Apps",
        routes=app.routes,
        servers=[
            {"url": "https://api.memobase.dev"},
            {"url": "https://api.memboase.cn"},
        ],
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

router = APIRouter(prefix="/api/v1")
LOGGING_CONFIG["formatters"]["default"][
    "fmt"
] = "%(levelprefix)s %(asctime)s %(message)s"
LOGGING_CONFIG["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"

LOGGING_CONFIG["formatters"]["default"][
    "fmt"
] = "%(levelprefix)s %(asctime)s %(message)s"
LOGGING_CONFIG["formatters"]["access"][
    "fmt"
] = "%(levelprefix)s %(asctime)s %(client_addr)s - %(request_line)s %(status_code)s"
LOGGING_CONFIG["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"
LOGGING_CONFIG["formatters"]["access"]["datefmt"] = "%Y-%m-%d %H:%M:%S"


@router.get("/healthcheck", tags=["chore"],
            openapi_extra={"x-code-samples": [
                {
                    "lang": "Python",
                    "source": "# To use the Python SDK, install the package:\n# pip install memobase\n\n from memobase import Memobase\n\n memobase = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')\n\n assert memobase.ping()\n\n",
                    "label": "Python"
                },
                {
                    "lang": "JavaScript",
                    "source": "// To use the JavaScript SDK, install the package:\n// npm install @memobase/memobase\n\n import { MemoBaseClient } from '@memobase/memobase';\n\n const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);\n\n await client.ping();\n\n",
                    "label": "JavaScript"
                },
                {
                    "lang": "Go",
                    "source": "// To use the Go SDK, install the package:\n// go get github.com/memodb-io/memobase/src/client/memobase-go@latest\n\nimport (\n\t\"github.com/memodb-io/memobase/src/client/memobase-go/core\"\n)\n\nprojectURL := \"YOUR_PROJECT_URL\"\napiKey := \"YOUR_API_KEY\"\nclient, err := core.NewMemoBaseClient(projectURL, apiKey)\nif err != nil {\n\tpanic(err)\n}\n\nok := client.Ping()\nif !ok {\n\tpanic(\"Failed to connect to Memobase\")\n}\n",
                    "label": "Go"
                }
            ]}
)
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


@router.post("/project/profile_config", tags=["project"],
             openapi_extra={"x-code-samples": [
                {
                    "lang": "Python",
                    "source": "# To use the Python SDK, install the package:\n# pip install memobase\n\n from memobase import Memobase\n\n memobase = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')\n\n memobase.update_config('your_profile_config')\n\n",
                    "label": "Python"
                },
                {
                    "lang": "JavaScript",
                    "source": "// To use the JavaScript SDK, install the package:\n// npm install @memobase/memobase\n\n import { MemoBaseClient } from '@memobase/memobase';\n\n const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);\n\n await client.updateConfig('your_profile_config');\n\n",
                    "label": "JavaScript"
                }
            ]}
)
async def update_project_profile_config(
    request: Request,
    profile_config: res.ProfileConfigData = Body(
        ..., description="The profile config to update"
    ),
) -> res.BaseResponse:
    project_id = request.state.memobase_project_id
    if not utils.is_valid_profile_config(profile_config.profile_config):
        return Promise.reject(CODE.BAD_REQUEST, "Invalid profile config").to_response(
            BaseResponse
        )
    p = await controllers.project.update_project_profile_config(
        project_id, profile_config.profile_config
    )
    return p.to_response(res.BaseResponse)


@router.get("/project/profile_config", tags=["project"],
             openapi_extra={"x-code-samples": [
                {
                    "lang": "Python",
                    "source": "# To use the Python SDK, install the package:\n# pip install memobase\n\n from memobase import Memobase\n\n memobase = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')\n\n config = memobase.get_config()\n\n",
                    "label": "Python"
                },
                {
                    "lang": "JavaScript",
                    "source": "// To use the JavaScript SDK, install the package:\n// npm install @memobase/memobase\n\n import { MemoBaseClient } from '@memobase/memobase';\n\n const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);\n\n const config = await client.getConfig();\n\n",
                    "label": "JavaScript"
                }
            ]}
)
async def get_project_profile_config_string(
    request: Request,
) -> res.ProfileConfigDataResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.project.get_project_profile_config_string(project_id)
    return p.to_response(res.ProfileConfigDataResponse)


@router.get("/project/billing", tags=["project"])
async def get_project_billing(request: Request) -> res.BillingResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.billing.get_project_billing(project_id)
    return p.to_response(res.BillingResponse)


@router.post("/users", tags=["user"],
             openapi_extra={"x-code-samples": [
                {
                    "lang": "Python",
                    "source": "# To use the Python SDK, install the package:\n# pip install memobase\n\n from memobase import Memobase\n\n client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')\n\n uid = client.add_user({\"ANY\": \"DATA\"})\n\n",
                    "label": "Python"
                },
                {
                    "lang": "JavaScript", 
                    "source": "// To use the JavaScript SDK, install the package:\n// npm install @memobase/memobase\n\n import { MemoBaseClient } from '@memobase/memobase';\n\n const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);\n\n const userId = await client.addUser({ANY: \"DATA\"});\n\n",
                    "label": "JavaScript"
                },
                {
                    "lang": "Go",
                    "source": "// To use the Go SDK, install the package:\n// go get github.com/memodb-io/memobase/src/client/memobase-go@latest\n\nimport (\n\t\"github.com/memodb-io/memobase/src/client/memobase-go/core\"\n\t\"github.com/google/uuid\"\n)\n\nprojectURL := \"YOUR_PROJECT_URL\"\napiKey := \"YOUR_API_KEY\"\nclient, err := core.NewMemoBaseClient(projectURL, apiKey)\nif err != nil {\n\tpanic(err)\n}\n\n// Generate a UUID for the user\nuserID := uuid.New().String()\n\n// Create user with some data\ndata := map[string]interface{}{\"ANY\": \"DATA\"}\nresultID, err := client.AddUser(data, userID)\nif err != nil {\n\tpanic(err)\n}\n",
                    "label": "Go"
                }
            ]}
)
async def create_user(
    request: Request,
    user_data: res.UserData = Body(
        ..., description="User data for creating a new user"
    ),
) -> res.IdResponse:
    """Create a new user with additional data"""
    project_id = request.state.memobase_project_id
    p = await controllers.user.create_user(user_data, project_id)
    return p.to_response(res.IdResponse)


@router.get("/users/{user_id}", tags=["user"],
             openapi_extra={"x-code-samples": [
                {
                    "lang": "Python",
                    "source": "# To use the Python SDK, install the package:\n# pip install memobase\n\n from memobase import Memobase\n\n client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')\n\n u = client.get_user(uid)\n\n",
                    "label": "Python"
                },
                {
                    "lang": "JavaScript",
                    "source": "// To use the JavaScript SDK, install the package:\n// npm install @memobase/memobase\n\n import { MemoBaseClient } from '@memobase/memobase';\n\n const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);\n\n const user = await client.getUser(userId);\n\n",
                    "label": "JavaScript"
                },
                {
                    "lang": "Go",
                    "source": "// To use the Go SDK, install the package:\n// go get github.com/memodb-io/memobase/src/client/memobase-go@latest\n\nimport (\n\t\"github.com/memodb-io/memobase/src/client/memobase-go/core\"\n)\n\nprojectURL := \"YOUR_PROJECT_URL\"\napiKey := \"YOUR_API_KEY\"\nclient, err := core.NewMemoBaseClient(projectURL, apiKey)\nif err != nil {\n\tpanic(err)\n}\n\n// Get user by ID\nuser, err := client.GetUser(userID)\nif err != nil {\n\tpanic(err)\n}\n\n// Access user data\nuserData := user.GetData()\n",
                    "label": "Go"
                }
            ]}
)
async def get_user(
    request: Request,
    user_id: str = Path(..., description="The ID of the user to retrieve"),
) -> res.UserDataResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.user.get_user(user_id, project_id)
    return p.to_response(res.UserDataResponse)


@router.put("/users/{user_id}", tags=["user"],
             openapi_extra={"x-code-samples": [
                {
                    "lang": "Python",
                    "source": "# To use the Python SDK, install the package:\n# pip install memobase\n\n from memobase import Memobase\n\n client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')\n\n client.update_user(uid, {\"ANY\": \"NEW_DATA\"})\n\n",
                    "label": "Python"
                },
                {
                    "lang": "JavaScript",
                    "source": "// To use the JavaScript SDK, install the package:\n// npm install @memobase/memobase\n\n import { MemoBaseClient } from '@memobase/memobase';\n\n const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);\n\n await client.updateUser(userId, {ANY: \"NEW_DATA\"});\n\n",
                    "label": "JavaScript"
                },
                {
                    "lang": "Go",
                    "source": "// To use the Go SDK, install the package:\n// go get github.com/memodb-io/memobase/src/client/memobase-go@latest\n\nimport (\n\t\"github.com/memodb-io/memobase/src/client/memobase-go/core\"\n)\n\nprojectURL := \"YOUR_PROJECT_URL\"\napiKey := \"YOUR_API_KEY\"\nclient, err := core.NewMemoBaseClient(projectURL, apiKey)\nif err != nil {\n\tpanic(err)\n}\n\n// Update user data\nnewData := map[string]interface{}{\"ANY\": \"NEW_DATA\"}\nerr = client.UpdateUser(userID, newData)\nif err != nil {\n\tpanic(err)\n}\n",
                    "label": "Go"
                }
            ]}
)
async def update_user(
    request: Request,
    user_id: str = Path(..., description="The ID of the user to update"),
    user_data: dict = Body(..., description="Updated user data"),
) -> res.IdResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.user.update_user(user_id, project_id, user_data)
    return p.to_response(res.IdResponse)


@router.delete("/users/{user_id}", tags=["user"],
             openapi_extra={"x-code-samples": [
                {
                    "lang": "Python",
                    "source": "# To use the Python SDK, install the package:\n# pip install memobase\n\n from memobase import Memobase\n\n client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')\n\n client.delete_user(uid)\n\n",
                    "label": "Python"
                },
                {
                    "lang": "JavaScript",
                    "source": "// To use the JavaScript SDK, install the package:\n// npm install @memobase/memobase\n\n import { MemoBaseClient } from '@memobase/memobase';\n\n const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);\n\n await client.deleteUser(userId);\n\n",
                    "label": "JavaScript"
                },
                {
                    "lang": "Go",
                    "source": "// To use the Go SDK, install the package:\n// go get github.com/memodb-io/memobase/src/client/memobase-go@latest\n\nimport (\n\t\"github.com/memodb-io/memobase/src/client/memobase-go/core\"\n)\n\nprojectURL := \"YOUR_PROJECT_URL\"\napiKey := \"YOUR_API_KEY\"\nclient, err := core.NewMemoBaseClient(projectURL, apiKey)\nif err != nil {\n\tpanic(err)\n}\n\n// Delete user\nerr = client.DeleteUser(userID)\nif err != nil {\n\tpanic(err)\n}\n",
                    "label": "Go"
                }
            ]}
)
async def delete_user(
    request: Request,
    user_id: str = Path(..., description="The ID of the user to delete"),
) -> BaseResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.user.delete_user(user_id, project_id)
    return p.to_response(BaseResponse)


@router.get("/users/blobs/{user_id}/{blob_type}", tags=["user"],
             openapi_extra={"x-code-samples": [
                {
                    "lang": "Python",
                    "source": "# To use the Python SDK, install the package:\n# pip install memobase\n\n from memobase import Memobase\n from memobase.core.types import BlobType\n\n memobase = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')\n\n user = memobase.get_user('user_id')\n blobs = user.get_all(BlobType.CHAT, page=0, page_size=10)\n\n",
                    "label": "Python"
                },
                {
                    "lang": "JavaScript",
                    "source": "// To use the JavaScript SDK, install the package:\n// npm install @memobase/memobase\n\n import { MemoBaseClient, BlobType } from '@memobase/memobase';\n\n const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);\n\n const user = client.getUser('user_id');\n const blobs = await user.getAll(BlobType.Enum.chat);\n\n",
                    "label": "JavaScript"
                },
                {
                    "lang": "Go",
                    "source": "// To use the Go SDK, install the package:\n// go get github.com/memodb-io/memobase/src/client/memobase-go@latest\n\nimport (\n\t\"github.com/memodb-io/memobase/src/client/memobase-go/core\"\n\t\"github.com/memodb-io/memobase/src/client/memobase-go/blob\"\n)\n\nprojectURL := \"YOUR_PROJECT_URL\"\napiKey := \"YOUR_API_KEY\"\nclient, err := core.NewMemoBaseClient(projectURL, apiKey)\nif err != nil {\n\tpanic(err)\n}\n\n// Get user\nuser, err := client.GetUser(userID)\nif err != nil {\n\tpanic(err)\n}\n\n// Get all blobs\nblobs, err := user.GetAll(blob.ChatType)\nif err != nil {\n\tpanic(err)\n}\n",
                    "label": "Go"
                }
            ]}
)
async def get_user_all_blobs(
    request: Request,
    user_id: str = Path(..., description="The ID of the user to fetch blobs for"),
    blob_type: BlobType = Path(..., description="The type of blobs to retrieve"),
    page: int = Query(0, description="Page number for pagination, starting from 0"),
    page_size: int = Query(10, description="Number of items per page, default is 10"),
) -> res.IdsResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.user.get_user_all_blobs(
        user_id, project_id, blob_type, page, page_size
    )
    return p.to_response(res.IdsResponse)


@router.post("/blobs/insert/{user_id}", tags=["blob"],
             openapi_extra={"x-code-samples": [
                {
                    "lang": "Python",
                    "source": "# To use the Python SDK, install the package:\n# pip install memobase\n\n from memobase import Memobase\n from memobase import ChatBlob\n\n client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')\n\n b = ChatBlob(messages=[\n    {\n        \"role\": \"user\",\n        \"content\": \"Hi, I'm here again\"\n    },\n    {\n        \"role\": \"assistant\",\n        \"content\": \"Hi, Gus! How can I help you?\"\n    }\n])\n u = client.get_user(uid)\n bid = u.insert(b)\n\n",
                    "label": "Python"
                },
                {
                    "lang": "JavaScript",
                    "source": "// To use the JavaScript SDK, install the package:\n// npm install @memobase/memobase\n\n import { MemoBaseClient, Blob, BlobType } from '@memobase/memobase';\n\n const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);\n const user = await client.getUser(userId);\n\n const blobId = await user.insert(Blob.parse({\n  type: BlobType.Enum.chat,\n  messages: [\n    {\n      role: 'user',\n      content: 'Hi, I\\'m here again'\n    },\n    {\n      role: 'assistant',\n      content: 'Hi, Gus! How can I help you?'\n    }\n  ]\n}));\n\n",
                    "label": "JavaScript"
                },
                {
                    "lang": "Go",
                    "source": "// To use the Go SDK, install the package:\n// go get github.com/memodb-io/memobase/src/client/memobase-go@latest\n\nimport (\n\t\"github.com/memodb-io/memobase/src/client/memobase-go/core\"\n\t\"github.com/memodb-io/memobase/src/client/memobase-go/blob\"\n)\n\nprojectURL := \"YOUR_PROJECT_URL\"\napiKey := \"YOUR_API_KEY\"\nclient, err := core.NewMemoBaseClient(projectURL, apiKey)\nif err != nil {\n\tpanic(err)\n}\n\n// Get user\nuser, err := client.GetUser(userID)\nif err != nil {\n\tpanic(err)\n}\n\n// Create chat blob\nchatBlob := &blob.ChatBlob{\n\tBaseBlob: blob.BaseBlob{\n\t\tType: blob.ChatType,\n\t},\n\tMessages: []blob.OpenAICompatibleMessage{\n\t\t{\n\t\t\tRole:    \"user\",\n\t\t\tContent: \"Hi, I'm here again\",\n\t\t},\n\t\t{\n\t\t\tRole:    \"assistant\",\n\t\t\tContent: \"Hi, Gus! How can I help you?\",\n\t\t},\n\t},\n}\n\n// Insert blob\nblobID, err := user.Insert(chatBlob)\nif err != nil {\n\tpanic(err)\n}\n",
                    "label": "Go"
                }
            ]}
)
async def insert_blob(
    request: Request,
    user_id: str = Path(..., description="The ID of the user to insert the blob for"),
    blob_data: res.BlobData = Body(..., description="The blob data to insert"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
) -> res.IdResponse:
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
        p = await controllers.blob.insert_blob(user_id, project_id, blob_data)
        if not p.ok():
            return p.to_response(res.IdResponse)

        # TODO if single user insert too fast will cause random order insert to buffer
        # So no background task for insert buffer yet
        pb = await controllers.buffer.insert_blob_to_buffer(
            user_id, project_id, p.data().id, blob_data.to_blob()
        )
        if not pb.ok():
            return pb.to_response(res.IdResponse)
    except Exception as e:
        LOG.error(f"Error inserting blob: {e}")
        return Promise.reject(
            CODE.INTERNAL_SERVER_ERROR, f"Error inserting blob: {e}"
        ).to_response(res.IdResponse)

    background_tasks.add_task(
        capture_int_key,
        TelemetryKeyName.insert_blob_success_request,
        project_id=project_id,
    )
    return p.to_response(res.IdResponse)


@router.get("/blobs/{user_id}/{blob_id}", tags=["blob"],
             openapi_extra={"x-code-samples": [
                {
                    "lang": "Python",
                    "source": "# To use the Python SDK, install the package:\n# pip install memobase\n\n from memobase import Memobase\n\n client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')\n\n u = client.get_user(uid)\n b = u.get(bid)\n\n",
                    "label": "Python"
                },
                {
                    "lang": "JavaScript",
                    "source": "// To use the JavaScript SDK, install the package:\n// npm install @memobase/memobase\n\n import { MemoBaseClient } from '@memobase/memobase';\n\n const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);\n const user = await client.getUser(userId);\n\n const blob = await user.get(blobId);\n\n",
                    "label": "JavaScript"
                },
                {
                    "lang": "Go",
                    "source": "// To use the Go SDK, install the package:\n// go get github.com/memodb-io/memobase/src/client/memobase-go@latest\n\nimport (\n\t\"github.com/memodb-io/memobase/src/client/memobase-go/core\"\n\t\"github.com/memodb-io/memobase/src/client/memobase-go/blob\"\n)\n\nprojectURL := \"YOUR_PROJECT_URL\"\napiKey := \"YOUR_API_KEY\"\nclient, err := core.NewMemoBaseClient(projectURL, apiKey)\nif err != nil {\n\tpanic(err)\n}\n\n// Get user\nuser, err := client.GetUser(userID)\nif err != nil {\n\tpanic(err)\n}\n\n// Get blob\nblob, err := user.Get(blobID)\nif err != nil {\n\tpanic(err)\n}\n\n// If it's a chat blob, you can access its messages\nif chatBlob, ok := blob.(*blob.ChatBlob); ok {\n\tmessages := chatBlob.Messages\n\t// Process messages\n}\n",
                    "label": "Go"
                }
            ]}
)
async def get_blob(
    request: Request,
    user_id: str = Path(..., description="The ID of the user"),
    blob_id: str = Path(..., description="The ID of the blob to retrieve"),
) -> res.BlobDataResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.blob.get_blob(user_id, project_id, blob_id)
    return p.to_response(res.BlobDataResponse)


@router.delete("/blobs/{user_id}/{blob_id}", tags=["blob"],
             openapi_extra={"x-code-samples": [
                {
                    "lang": "Python",
                    "source": "# To use the Python SDK, install the package:\n# pip install memobase\n\n from memobase import Memobase\n\n client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')\n\n u = client.get_user(uid)\n u.delete(bid)\n\n",
                    "label": "Python"
                },
                {
                    "lang": "JavaScript",
                    "source": "// To use the JavaScript SDK, install the package:\n// npm install @memobase/memobase\n\n import { MemoBaseClient } from '@memobase/memobase';\n\n const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);\n const user = await client.getUser(userId);\n\n await user.delete(blobId);\n\n",
                    "label": "JavaScript"
                },
                {
                    "lang": "Go",
                    "source": "// To use the Go SDK, install the package:\n// go get github.com/memodb-io/memobase/src/client/memobase-go@latest\n\nimport (\n\t\"github.com/memodb-io/memobase/src/client/memobase-go/core\"\n)\n\nprojectURL := \"YOUR_PROJECT_URL\"\napiKey := \"YOUR_API_KEY\"\nclient, err := core.NewMemoBaseClient(projectURL, apiKey)\nif err != nil {\n\tpanic(err)\n}\n\n// Get user\nuser, err := client.GetUser(userID)\nif err != nil {\n\tpanic(err)\n}\n\n// Delete blob\nerr = user.Delete(blobID)\nif err != nil {\n\tpanic(err)\n}\n",
                    "label": "Go"
                }
            ]}
)
async def delete_blob(
    request: Request,
    user_id: str = Path(..., description="The ID of the user"),
    blob_id: str = Path(..., description="The ID of the blob to delete"),
) -> res.BaseResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.blob.remove_blob(user_id, project_id, blob_id)
    return p.to_response(res.BaseResponse)


@router.get("/users/profile/{user_id}", tags=["profile"],
             openapi_extra={"x-code-samples": [
                {
                    "lang": "Python",
                    "source": "# To use the Python SDK, install the package:\n# pip install memobase\n\n from memobase import Memobase\n\n client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')\n\n u = client.get_user(uid)\n p = u.profile()\n\n",
                    "label": "Python"
                },
                {
                    "lang": "JavaScript",
                    "source": "// To use the JavaScript SDK, install the package:\n// npm install @memobase/memobase\n\n import { MemoBaseClient } from '@memobase/memobase';\n\n const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);\n const user = await client.getUser(userId);\n\n const profiles = await user.profile();\n\n",
                    "label": "JavaScript"
                },
                {
                    "lang": "Go",
                    "source": "// To use the Go SDK, install the package:\n// go get github.com/memodb-io/memobase/src/client/memobase-go@latest\n\nimport (\n\t\"github.com/memodb-io/memobase/src/client/memobase-go/core\"\n)\n\nprojectURL := \"YOUR_PROJECT_URL\"\napiKey := \"YOUR_API_KEY\"\nclient, err := core.NewMemoBaseClient(projectURL, apiKey)\nif err != nil {\n\tpanic(err)\n}\n\n// Get user\nuser, err := client.GetUser(userID)\nif err != nil {\n\tpanic(err)\n}\n\n// Get profile\nprofiles, err := user.Profile()\nif err != nil {\n\tpanic(err)\n}\n",
                    "label": "Go"
                }
            ]}
)
async def get_user_profile(
    request: Request,
    user_id: str = Path(..., description="The ID of the user to get profiles for"),
    topk: int = Query(
        None, description="Number of profiles to retrieve, default is all"
    ),
    max_token_size: int = Query(
        None,
        description="Max token size of returned profile content, default is all",
    ),
    prefer_topics: list[str] = Query(
        None,
        description="Rank prefer topics at first to try to keep them in filtering, default order is by updated time",
    ),
    only_topics: list[str] = Query(
        None,
        description="Only return profiles with these topics, default is all",
    ),
    max_subtopic_size: int = Query(
        None,
        description="Max subtopic size of the same topic in returned profile, default is all",
    ),
    topic_limits_json: str = Query(
        None,
        description='Set specific subtopic limits for topics in JSON, for example {"topic1": 3, "topic2": 5}. The limits in this param will override `max_subtopic_size`.',
    ),
) -> res.UserProfileResponse:
    """Get the real-time user profiles for long term memory"""
    project_id = request.state.memobase_project_id
    topic_limits_json = topic_limits_json or "{}"
    try:
        topic_limits = res.StrIntData(data=json.loads(topic_limits_json)).data
    except Exception as e:
        return Promise.reject(
            CODE.BAD_REQUEST, f"Invalid topic_limits JSON: {e}"
        ).to_response(res.UserProfileResponse)
    p = await controllers.profile.get_user_profiles(user_id, project_id)
    p = await controllers.profile.truncate_profiles(
        p.data(),
        prefer_topics=prefer_topics,
        topk=topk,
        max_token_size=max_token_size,
        only_topics=only_topics,
        max_subtopic_size=max_subtopic_size,
        topic_limits=topic_limits,
    )
    return p.to_response(res.UserProfileResponse)


@router.post("/users/buffer/{user_id}/{buffer_type}", tags=["buffer"],
             openapi_extra={"x-code-samples": [
                {
                    "lang": "Python",
                    "source": "# To use the Python SDK, install the package:\n# pip install memobase\n\n from memobase import Memobase\n\n client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')\n\n u.flush()\n\n",
                    "label": "Python"
                },
                {
                    "lang": "JavaScript",
                    "source": "// To use the JavaScript SDK, install the package:\n// npm install @memobase/memobase\n\n import { MemoBaseClient, BlobType } from '@memobase/memobase';\n\n const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);\n const user = await client.getUser(userId);\n\n await user.flush(BlobType.Enum.chat);\n\n",
                    "label": "JavaScript"
                },
                {
                    "lang": "Go",
                    "source": "// To use the Go SDK, install the package:\n// go get github.com/memodb-io/memobase/src/client/memobase-go@latest\n\nimport (\n\t\"github.com/memodb-io/memobase/src/client/memobase-go/core\"\n\t\"github.com/memodb-io/memobase/src/client/memobase-go/blob\"\n)\n\nprojectURL := \"YOUR_PROJECT_URL\"\napiKey := \"YOUR_API_KEY\"\nclient, err := core.NewMemoBaseClient(projectURL, apiKey)\nif err != nil {\n\tpanic(err)\n}\n\n// Get user\nuser, err := client.GetUser(userID)\nif err != nil {\n\tpanic(err)\n}\n\n// Flush buffer\nerr = user.Flush(blob.ChatType)\nif err != nil {\n\tpanic(err)\n}\n",
                    "label": "Go"
                }
            ]}
)
async def flush_buffer(
    request: Request,
    user_id: str = Path(..., description="The ID of the user"),
    buffer_type: BlobType = Path(..., description="The type of buffer to flush"),
) -> res.BaseResponse:
    """Get the real-time user profiles for long term memory"""
    project_id = request.state.memobase_project_id
    p = await controllers.buffer.wait_insert_done_then_flush(
        user_id, project_id, buffer_type
    )
    return p.to_response(res.BaseResponse)


@router.delete("/users/profile/{user_id}/{profile_id}", tags=["profile"],
             openapi_extra={"x-code-samples": [
                {
                    "lang": "Python",
                    "source": "# To use the Python SDK, install the package:\n# pip install memobase\n\n from memobase import Memobase\n\n memobase = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')\n\n memobase.delete_profile('user_id', 'profile_id')\n\n",
                    "label": "Python"
                },
                {
                    "lang": "JavaScript",
                    "source": "// To use the JavaScript SDK, install the package:\n// npm install @memobase/memobase\n\n import { MemoBaseClient } from '@memobase/memobase';\n\n const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);\n\n await client.deleteProfile('user_id', 'profile_id');\n\n",
                    "label": "JavaScript"
                },
                {
                    "lang": "Go",
                    "source": "// To use the Go SDK, install the package:\n// go get github.com/memodb-io/memobase/src/client/memobase-go@latest\n\nimport (\n\t\"github.com/memodb-io/memobase/src/client/memobase-go/core\"\n)\n\nprojectURL := \"YOUR_PROJECT_URL\"\napiKey := \"YOUR_API_KEY\"\nclient, err := core.NewMemoBaseClient(projectURL, apiKey)\nif err != nil {\n\tpanic(err)\n}\n\n// Get user\nuser, err := client.GetUser(userID)\nif err != nil {\n\tpanic(err)\n}\n\n// Delete profile\nerr = user.DeleteProfile(profileID)\nif err != nil {\n\tpanic(err)\n}\n",
                    "label": "Go"
                }
            ]}
)
async def delete_user_profile(
    request: Request,
    user_id: str = Path(..., description="The ID of the user"),
    profile_id: str = Path(..., description="The ID of the profile to delete"),
) -> res.BaseResponse:
    """Get the real-time user profiles for long term memory"""
    project_id = request.state.memobase_project_id
    p = await controllers.profile.delete_user_profile(user_id, project_id, profile_id)
    return p.to_response(res.IdResponse)


@router.get("/users/event/{user_id}", tags=["event"],
             openapi_extra={"x-code-samples": [
                {
                    "lang": "Python",
                    "source": "# To use the Python SDK, install the package:\n# pip install memobase\n\n from memobase import Memobase\n\n client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')\n\n events = u.event(topk=10, max_token_size=1000)\n\n",
                    "label": "Python"
                },
                {
                    "lang": "JavaScript",
                    "source": "// To use the JavaScript SDK, install the package:\n// npm install @memobase/memobase\n\n import { MemoBaseClient } from '@memobase/memobase';\n\n const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);\n const user = await client.getUser(userId);\n\n const events = await user.event();\n\n",
                    "label": "JavaScript"
                }
            ]}
)
async def get_user_events(
    request: Request,
    user_id: str = Path(..., description="The ID of the user"),
    topk: int = Query(10, description="Number of events to retrieve, default is 10"),
    max_token_size: int = Query(
        None,
        description="Max token size of returned events",
    ),
) -> res.UserEventsDataResponse:
    project_id = request.state.memobase_project_id
    p = await controllers.event.get_user_events(
        user_id, project_id, topk=topk, max_token_size=max_token_size
    )
    return p.to_response(res.UserEventsDataResponse)


@router.get("/users/context/{user_id}", tags=["context"],
             openapi_extra={"x-code-samples": [
                {
                    "lang": "Python",
                    "source": "# To use the Python SDK, install the package:\n# pip install memobase\n\n from memobase import Memobase\n\n client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')\n\n context = u.context(max_token_size=1000, \n                    prefer_topics=['work', 'family'], \n                    only_topics=None, \n                    max_subtopic_size=5, \n                    topic_limits={'work': 3, 'family': 2}, \n                    profile_event_ratio=0.8)\n\n",
                    "label": "Python"
                },
                {
                    "lang": "JavaScript",
                    "source": "// To use the JavaScript SDK, install the package:\n// npm install @memobase/memobase\n\n import { MemoBaseClient } from '@memobase/memobase';\n\n const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);\n const user = await client.getUser(userId);\n\n const context = await user.context({\n  maxTokenSize: 1000,\n  preferTopics: ['work', 'family'],\n  onlyTopics: null,\n  maxSubtopicSize: 5,\n  topicLimits: {work: 3, family: 2},\n  profileEventRatio: 0.8\n});\n\n",
                    "label": "JavaScript"
                }
            ]}
)
async def get_user_context(
    request: Request,
    user_id: str = Path(..., description="The ID of the user"),
    max_token_size: int = Query(
        1000,
        description="Max token size of returned Context",
    ),
    prefer_topics: list[str] = Query(
        None,
        description="Rank prefer topics at first to try to keep them in filtering, default order is by updated time",
    ),
    only_topics: list[str] = Query(
        None,
        description="Only return profiles with these topics, default is all",
    ),
    max_subtopic_size: int = Query(
        None,
        description="Max subtopic size of the same topic in returned Context",
    ),
    topic_limits_json: str = Query(
        None,
        description='Set specific subtopic limits for topics in JSON, for example {"topic1": 3, "topic2": 5}. The limits in this param will override `max_subtopic_size`.',
    ),
    profile_event_ratio: float = Query(
        0.8,
        description="Profile event ratio of returned Context",
    ),
) -> res.UserContextDataResponse:
    project_id = request.state.memobase_project_id
    topic_limits_json = topic_limits_json or "{}"
    try:
        topic_limits = res.StrIntData(data=json.loads(topic_limits_json)).data
    except Exception as e:
        return Promise.reject(
            CODE.BAD_REQUEST, f"Invalid topic_limits JSON: {e}"
        ).to_response(res.UserProfileResponse)
    p = await controllers.context.get_user_context(
        user_id,
        project_id,
        max_token_size,
        prefer_topics,
        only_topics,
        max_subtopic_size,
        topic_limits,
        profile_event_ratio,
    )
    return p.to_response(res.UserContextDataResponse)


PATH_MAPPINGS = [
    "/api/v1/users/blobs",
    "/api/v1/users/profile",
    "/api/v1/users/buffer",
    "/api/v1/users/event",
    "/api/v1/users/context",
    "/api/v1/users",
    "/api/v1/blobs/insert",
    "/api/v1/blobs",
]


class AuthMiddleware(BaseHTTPMiddleware):
    def normalize_path(self, path: str) -> str:
        """Remove dynamic path parameters to get normalized path for metrics"""
        if not path.startswith("/api"):
            return path

        for prefix in PATH_MAPPINGS:
            if path.startswith(prefix):
                return prefix

        return path

    async def dispatch(self, request, call_next):
        if not request.url.path.startswith("/api"):
            return await call_next(request)

        if request.url.path.startswith("/api/v1/healthcheck"):
            telemetry_manager.increment_counter_metric(
                CounterMetricName.HEALTHCHECK,
                1,
            )
            return await call_next(request)

        auth_token = request.headers.get("Authorization")
        if not auth_token or not auth_token.startswith("Bearer "):
            return JSONResponse(
                status_code=CODE.UNAUTHORIZED.value,
                content=BaseResponse(
                    errno=CODE.UNAUTHORIZED.value,
                    errmsg=f"Unauthorized access to {request.url.path}. You have to provide a valid Bearer token.",
                ).model_dump(),
            )
        auth_token = (auth_token.split(" ")[1]).strip()
        is_root = self.is_valid_root(auth_token)
        request.state.is_memobase_root = is_root
        request.state.memobase_project_id = DEFAULT_PROJECT_ID
        if not is_root:
            p = await self.parse_project_token(auth_token)
            if not p.ok():
                return JSONResponse(
                    status_code=CODE.UNAUTHORIZED.value,
                    content=BaseResponse(
                        errno=CODE.UNAUTHORIZED.value,
                        errmsg=f"Unauthorized access to {request.url.path}. {p.msg()}",
                    ).model_dump(),
                )
            request.state.memobase_project_id = p.data()
        # await capture_int_key(TelemetryKeyName.has_request)

        normalized_path = self.normalize_path(request.url.path)

        telemetry_manager.increment_counter_metric(
            CounterMetricName.REQUEST,
            1,
            {
                "project_id": request.state.memobase_project_id,
                "path": normalized_path,
                "method": request.method,
            },
        )

        start_time = time.time()
        response = await call_next(request)

        telemetry_manager.record_histogram_metric(
            HistogramMetricName.REQUEST_LATENCY_MS,
            (time.time() - start_time) * 1000,
            {
                "project_id": request.state.memobase_project_id,
                "path": normalized_path,
                "method": request.method,
            },
        )
        return response

    def is_valid_root(self, token: str) -> bool:
        access_token = os.getenv("ACCESS_TOKEN")
        if access_token is None:
            return True
        return token == access_token.strip()

    async def parse_project_token(self, token: str) -> Promise[str]:
        p = parse_project_id(token)
        if not p.ok():
            return Promise.reject(CODE.UNAUTHORIZED, "Invalid project id format")
        project_id = p.data()
        p = await check_project_secret(project_id, token)
        if not p.ok():
            return p
        if not p.data():
            return Promise.reject(CODE.UNAUTHORIZED, "Wrong secret key")
        p = await get_project_status(project_id)
        if not p.ok():
            return p
        if p.data() == ProjectStatus.suspended:
            return Promise.reject(CODE.FORBIDDEN, "Your project is suspended!")
        return Promise.resolve(project_id)


app.include_router(router)
app.add_middleware(AuthMiddleware)
