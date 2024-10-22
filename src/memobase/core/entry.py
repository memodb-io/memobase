import os
import httpx
from typing import Optional
from pydantic import BaseModel, Field, field_validator, HttpUrl
from dataclasses import dataclass
from .blob import BlobType, Blob
from .type import BaseResponse
from ..network import unpack_response
from ..error import ServerError


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

    def healthcheck(self) -> bool:
        r = unpack_response(self._client.get("/healthcheck"))
        return r.errno == 0

    def add_user(self, data: dict = None) -> str:
        r = unpack_response(self._client.post("/users", json={"data": data}))
        r.raise_for_status()
        return r.data["id"]

    def update_user(self, user_id: str, data: dict = None) -> str:
        r = unpack_response(self._client.put(f"/users/{user_id}", json={"data": data}))
        r.raise_for_status()
        return r.data["id"]

    def get_user(self, user_id: str) -> "User":
        r = unpack_response(self._client.get(f"/users/{user_id}"))
        r.raise_for_status()
        return User(
            user_id=user_id,
            project_client=self,
            fields=r.data,
        )

    def delete_user(self, user_id: str) -> bool:
        r = unpack_response(self._client.delete(f"/users/{user_id}"))
        r.raise_for_status()
        return True


@dataclass
class User:
    user_id: str
    project_client: MemoBaseClient
    fields: Optional[dict] = None

    def insert(self, blob_data: Blob) -> str:
        pass

    def get(self, blob_id: str) -> Blob:
        pass

    def query(self, query: str) -> list[Blob]:
        raise NotImplementedError("Query not yet ready")

    def persona_claims(self) -> list:
        raise NotImplementedError("persona_claims not yet ready")


a = MemoBaseClient(
    project_url="http://localhost:8000/",
    api_key="secret",
)
print(a)
print(a.healthcheck())
u = a.add_user()
print(u)
print(a.get_user(u))
print(a.update_user(u, {"test": 111}))
print(a.get_user(u).fields)
print(a.delete_user(u))
print(a.get_user(u))
