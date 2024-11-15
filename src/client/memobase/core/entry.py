import os
import httpx
from typing import Optional
from pydantic import HttpUrl
from dataclasses import dataclass
from .blob import BlobData, Blob, BlobType, ChatBlob
from .user import UserProfile, UserProfileData
from ..network import unpack_response
from ..error import ServerError
from ..utils import LOG


@dataclass
class MemoBaseClient:
    project_url: str
    api_key: Optional[str] = None
    api_version: str = "api/v1"

    def __post_init__(self):
        self.api_key = self.api_key or os.getenv("MEMOBASE_API_KEY")
        assert (
            self.api_key is not None
        ), "api_key of memobase client is required, pass it as argument or set it as environment variable(MEMOBASE_API_KEY)"
        self.base_url = str(HttpUrl(self.project_url)) + self.api_version.strip("/")

        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
            },
            timeout=60,
        )

    @property
    def client(self) -> httpx.Client:
        return self._client

    def ping(self) -> bool:
        try:
            unpack_response(self._client.get("/healthcheck"))
        except httpx.HTTPStatusError as e:
            LOG.error(f"Healthcheck failed: {e}")
            return False
        except ServerError as e:
            LOG.error(f"Healthcheck failed: {e}")
            return False
        return True

    def add_user(self, data: dict = None) -> str:
        r = unpack_response(self._client.post("/users", json={"data": data}))
        return r.data["id"]

    def update_user(self, user_id: str, data: dict = None) -> str:
        r = unpack_response(self._client.put(f"/users/{user_id}", json={"data": data}))
        return r.data["id"]

    def get_user(self, user_id: str, no_get=False) -> "User":
        if not no_get:
            r = unpack_response(self._client.get(f"/users/{user_id}"))
            return User(
                user_id=user_id,
                project_client=self,
                fields=r.data,
            )
        return User(user_id=user_id, project_client=self)

    def delete_user(self, user_id: str) -> bool:
        r = unpack_response(self._client.delete(f"/users/{user_id}"))
        return True


@dataclass
class User:
    user_id: str
    project_client: MemoBaseClient
    fields: Optional[dict] = None

    def insert(self, blob_data: Blob) -> str:
        r = unpack_response(
            self.project_client.client.post(
                f"/blobs/insert/{self.user_id}",
                json=blob_data.to_request(),
            )
        )
        return r.data["id"]

    def get(self, blob_id: str) -> Blob:
        r = unpack_response(
            self.project_client.client.get(f"/blobs/{self.user_id}/{blob_id}")
        )
        return BlobData.model_validate(r.data).to_blob()

    def delete(self, blob_id: str) -> bool:
        r = unpack_response(
            self.project_client.client.delete(f"/blobs/{self.user_id}/{blob_id}")
        )
        return True

    def flush(self, blob_type: BlobType = BlobType.chat) -> bool:
        r = unpack_response(
            self.project_client.client.post(f"/users/buffer/{self.user_id}/{blob_type}")
        )
        return True

    def profile(self) -> list[UserProfile]:
        r = unpack_response(
            self.project_client.client.get(f"/users/profile/{self.user_id}")
        )
        data = r.data["profiles"]
        return [UserProfileData.model_validate(p).to_ds() for p in data]
