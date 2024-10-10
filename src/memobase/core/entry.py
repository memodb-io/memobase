import os
from typing import Optional, Annotated
from pydantic import BaseModel, Field, field_validator, HttpUrl
from .blob import BlobType, Blob
from ..network import api_request
from ..error import ServerError


class User(BaseModel):
    project_url: HttpUrl = Field(description="Endpoint URL of the memobase project")
    api_key: str
    user_id: int
    fields: Optional[dict] = None

    def insert(self, blob_data: Blob) -> int:
        pass

    def get(self, blob_id: int) -> Blob:
        pass

    def query(self, query: str) -> list[Blob]:
        raise NotImplementedError("Query not yet ready")

    def persona_claims(self) -> list:
        raise NotImplementedError("persona_claims not yet ready")


class MemoBaseClient(BaseModel):
    project_url: Annotated[
        HttpUrl, Field(description="Endpoint URL of the memobase project")
    ]
    api_key: Annotated[Optional[str], Field(validate_default=True)] = None

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v):
        v = v or os.getenv("MEMOBASE_API_KEY")
        assert (
            v is not None
        ), "api_key of memobase client is required, pass it as argument or set it as environment variable(MEMOBASE_API_KEY)"
        return v

    def healthcheck(self) -> bool:
        result = api_request(
            str(self.project_url),
            "/healthcheck",
            "get",
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        return result.errno == 0

    def add_user(self, data: dict = None) -> int:
        result = api_request(
            str(self.project_url),
            "/users",
            "post",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"data": data},
        )
        if result.errno != 0:
            raise ServerError(result.errmsg)
        return result.data["id"]

    def update_user(self, user_id: int, data: dict = None) -> int:
        result = api_request(
            str(self.project_url),
            f"/users/{user_id}",
            "put",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"data": data},
        )
        if result.errno != 0:
            raise ServerError(result.errmsg)
        return result.data["id"]

    def get_user(self, user_id: int) -> User:
        result = api_request(
            str(self.project_url),
            f"/users/{user_id}",
            "get",
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        if result.errno != 0:
            raise ServerError(result.errmsg)
        return User(
            project_url=self.project_url,
            api_key=self.api_key,
            user_id=user_id,
            fields=result.data,
        )

    def delete_user(self, user_id: int) -> bool:
        result = api_request(
            str(self.project_url),
            f"/users/{user_id}",
            "delete",
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        if result.errno != 0:
            raise ServerError(result.errmsg)
        return True


a = MemoBaseClient(
    project_url="http://localhost:8000",
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
