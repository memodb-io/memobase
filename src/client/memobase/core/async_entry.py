import os
import json
import httpx
from collections import defaultdict
from typing import Optional, Literal
from pydantic import HttpUrl, ValidationError
from dataclasses import dataclass
from urllib.parse import quote_plus
from .blob import BlobData, Blob, BlobType, ChatBlob, OpenAICompatibleMessage
from .user import UserProfile, UserProfileData, UserEventData, UserEventGistData
from ..network import unpack_response
from ..error import ServerError
from ..utils import LOG


def profiles_to_json(profiles: list[UserProfile]) -> dict:
    results = defaultdict(dict)
    for p in profiles:
        results[p.topic][p.sub_topic] = {
            "id": p.id,
            "content": p.content,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
        }
    return dict(results)


@dataclass
class AsyncMemoBaseClient:
    api_key: Optional[str] = None
    api_version: str = "api/v1"
    project_url: str = "https://api.memobase.dev"

    def __post_init__(self):
        self.api_key = self.api_key or os.getenv("MEMOBASE_API_KEY")
        assert (
            self.api_key is not None
        ), "api_key of memobase client is required, pass it as argument or set it as environment variable(MEMOBASE_API_KEY)"
        self.base_url = str(HttpUrl(self.project_url)) + self.api_version.strip("/")

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
            },
            timeout=60,
        )

    @property
    def client(self) -> httpx.AsyncClient:
        return self._client

    async def ping(self) -> bool:
        try:
            unpack_response(await self._client.get("/healthcheck"))
        except httpx.HTTPStatusError as e:
            LOG.error(f"Healthcheck failed: {e}")
            return False
        except ServerError as e:
            LOG.error(f"Healthcheck failed: {e}")
            return False
        return True

    async def get_usage(self) -> dict:
        r = unpack_response(await self._client.get("/project/billing"))
        return r.data

    async def get_config(self) -> str:
        r = unpack_response(await self._client.get("/project/profile_config"))
        return r.data["profile_config"]

    async def update_config(self, config: str) -> bool:
        r = unpack_response(
            await self._client.post(
                "/project/profile_config", json={"profile_config": config}
            )
        )
        return True

    async def add_user(self, data: dict = None, id=None) -> str:
        r = unpack_response(
            await self._client.post("/users", json={"data": data, "id": id})
        )
        return r.data["id"]

    async def update_user(self, user_id: str, data: dict = None) -> str:
        r = unpack_response(
            await self._client.put(f"/users/{user_id}", json={"data": data})
        )
        return r.data["id"]

    async def get_user(self, user_id: str, no_get=False) -> "AsyncUser":
        if not no_get:
            r = unpack_response(await self._client.get(f"/users/{user_id}"))
            return AsyncUser(
                user_id=user_id,
                project_client=self,
                fields=r.data,
            )
        return AsyncUser(user_id=user_id, project_client=self)

    async def get_or_create_user(self, user_id: str) -> "AsyncUser":
        try:
            return await self.get_user(user_id)
        except ServerError:
            await self.add_user(id=user_id)
        return AsyncUser(user_id=user_id, project_client=self)

    async def delete_user(self, user_id: str) -> bool:
        r = unpack_response(await self._client.delete(f"/users/{user_id}"))
        return True

    async def get_all_users(
        self,
        search: str = "",
        order_by: str = "updated_at",
        order_desc: bool = True,
        limit: int = 10,
        offset: int = 0,
    ) -> list[dict]:
        r = unpack_response(
            await self._client.get(
                f"/project/users?search={search}&order_by={order_by}&order_desc={order_desc}&limit={limit}&offset={offset}"
            )
        )
        return r.data["users"]

    async def get_daily_usage(self, days: int = 7) -> dict:
        r = unpack_response(await self._client.get(f"/project/usage?last_days={days}"))
        return r.data

    async def close(self):
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


@dataclass
class AsyncUser:
    user_id: str
    project_client: AsyncMemoBaseClient
    fields: Optional[dict] = None

    async def insert(self, blob_data: Blob, sync=False) -> str:
        r = unpack_response(
            await self.project_client.client.post(
                f"/blobs/insert/{self.user_id}?wait_process={sync}",
                json=blob_data.to_request(),
            )
        )
        return r.data["id"]

    async def get(self, blob_id: str) -> Blob:
        r = unpack_response(
            await self.project_client.client.get(f"/blobs/{self.user_id}/{blob_id}")
        )
        return BlobData.model_validate(r.data).to_blob()

    async def get_all(
        self, blob_type: BlobType, page: int = 0, page_size: int = 10
    ) -> list[str]:
        r = unpack_response(
            await self.project_client.client.get(
                f"/users/blobs/{self.user_id}/{blob_type}?page={page}&page_size={page_size}"
            )
        )
        return r.data["ids"]

    async def delete(self, blob_id: str) -> bool:
        r = unpack_response(
            await self.project_client.client.delete(f"/blobs/{self.user_id}/{blob_id}")
        )
        return True

    async def flush(self, blob_type: BlobType = BlobType.chat, sync=False) -> bool:
        r = unpack_response(
            await self.project_client.client.post(
                f"/users/buffer/{self.user_id}/{blob_type}?wait_process={sync}"
            )
        )
        return True

    async def add_profile(self, content: str, topic: str, sub_topic: str) -> str:
        r = unpack_response(
            await self.project_client.client.post(
                f"/users/profile/{self.user_id}",
                json={
                    "content": content,
                    "attributes": {"topic": topic, "sub_topic": sub_topic},
                },
            )
        )
        return r.data["id"]

    async def buffer(
        self,
        blob_type: BlobType,
        status: Literal["idle", "processing", "done", "failed"] = "idle",
    ) -> list[str]:
        r = unpack_response(
            await self.project_client.client.get(
                f"/users/buffer/capacity/{self.user_id}/{blob_type}?status={status}"
            )
        )
        return r.data["ids"]

    async def profile(
        self,
        max_token_size: int = 1000,
        prefer_topics: list[str] = None,
        only_topics: list[str] = None,
        max_subtopic_size: int = None,
        topic_limits: dict[str, int] = None,
        chats: list[OpenAICompatibleMessage] = None,
        need_json: bool = False,
    ) -> list[UserProfile]:
        params = f"?max_token_size={max_token_size}"
        if prefer_topics:
            prefer_topics_query = [f"&prefer_topics={pt}" for pt in prefer_topics]
            params += "&".join(prefer_topics_query)
        if only_topics:
            only_topics_query = [f"&only_topics={ot}" for ot in only_topics]
            params += "&".join(only_topics_query)
        if max_subtopic_size:
            params += f"&max_subtopic_size={max_subtopic_size}"
        if topic_limits:
            params += f"&topic_limits_json={json.dumps(topic_limits)}"
        if chats:
            for c in chats:
                try:
                    OpenAICompatibleMessage(**c)
                except ValidationError as e:
                    raise ValueError(f"Invalid chat message: {e}")
            chats_query = f"&chats_str={json.dumps(chats)}"
            params += chats_query
        r = unpack_response(
            await self.project_client.client.get(
                f"/users/profile/{self.user_id}{params}"
            )
        )
        data = r.data["profiles"]
        ds_profiles = [UserProfileData.model_validate(p).to_ds() for p in data]
        if need_json:
            return profiles_to_json(ds_profiles)
        return ds_profiles

    async def update_profile(
        self, profile_id: str, content: str, topic: str, sub_topic: str
    ) -> str:
        r = unpack_response(
            await self.project_client.client.put(
                f"/users/profile/{self.user_id}/{profile_id}",
                json={
                    "content": content,
                    "attributes": {"topic": topic, "sub_topic": sub_topic},
                },
            )
        )
        return True

    async def delete_profile(self, profile_id: str) -> bool:
        r = unpack_response(
            await self.project_client.client.delete(
                f"/users/profile/{self.user_id}/{profile_id}"
            )
        )
        return True

    async def event(
        self, topk=10, max_token_size=None, need_summary=False
    ) -> list[UserEventData]:
        params = f"?topk={topk}"
        if max_token_size is not None:
            params += f"&max_token_size={max_token_size}"
        if need_summary:
            params += f"&need_summary=true"
        r = unpack_response(
            await self.project_client.client.get(f"/users/event/{self.user_id}{params}")
        )
        return [UserEventData.model_validate(e) for e in r.data["events"]]

    async def delete_event(self, event_id: str) -> bool:
        r = unpack_response(
            await self.project_client.client.delete(
                f"/users/event/{self.user_id}/{event_id}"
            )
        )
        return True

    async def update_event(self, event_id: str, event_data: dict) -> bool:
        r = unpack_response(
            await self.project_client.client.put(
                f"/users/event/{self.user_id}/{event_id}", json=event_data
            )
        )
        return True

    async def search_event(
        self,
        query: str,
        topk: int = 10,
        similarity_threshold: float = 0.5,
        time_range_in_days: int = 180,
    ) -> list[UserEventData]:
        params = f"?query={query}&topk={topk}&similarity_threshold={similarity_threshold}&time_range_in_days={time_range_in_days}"
        r = unpack_response(
            await self.project_client.client.get(
                f"/users/event/search/{self.user_id}{params}"
            )
        )
        return [UserEventData.model_validate(e) for e in r.data["events"]]

    async def search_event_gist(
        self,
        query: str,
        topk: int = 10,
        similarity_threshold: float = 0.2,
        time_range_in_days: int = 180,
    ) -> list[UserEventData]:
        params = f"?query={query}&topk={topk}&similarity_threshold={similarity_threshold}&time_range_in_days={time_range_in_days}"
        r = unpack_response(
            self.project_client.client.get(
                f"/users/event_gist/search/{self.user_id}{params}"
            )
        )
        return [UserEventGistData.model_validate(e) for e in r.data["gists"]]

    async def context(
        self,
        max_token_size: int = 1000,
        prefer_topics: list[str] = None,
        only_topics: list[str] = None,
        max_subtopic_size: int = None,
        topic_limits: dict[str, int] = None,
        profile_event_ratio: float = None,
        require_event_summary: bool = None,
        chats: list[OpenAICompatibleMessage] = None,
        event_similarity_threshold: float = None,
        customize_context_prompt: str = None,
        full_profile_and_only_search_event: bool = None,
        fill_window_with_events: bool = None,
    ) -> str:
        params = f"?max_token_size={max_token_size}"
        if prefer_topics:
            prefer_topics_query = [f"&prefer_topics={pt}" for pt in prefer_topics]
            params += "&".join(prefer_topics_query)
        if only_topics:
            only_topics_query = [f"&only_topics={ot}" for ot in only_topics]
            params += "&".join(only_topics_query)
        if max_subtopic_size:
            params += f"&max_subtopic_size={max_subtopic_size}"
        if topic_limits:
            params += f"&topic_limits_json={json.dumps(topic_limits)}"
        if profile_event_ratio:
            params += f"&profile_event_ratio={profile_event_ratio}"
        if require_event_summary is not None:
            params += (
                f"&require_event_summary={'true' if require_event_summary else 'false'}"
            )
        if chats:
            for c in chats:
                try:
                    OpenAICompatibleMessage(**c)
                except ValidationError as e:
                    raise ValueError(f"Invalid chat message: {e}")
            chats_query = f"&chats_str={json.dumps(chats)}"
            params += chats_query
        if event_similarity_threshold:
            params += f"&event_similarity_threshold={event_similarity_threshold}"
        if customize_context_prompt:
            params += (
                f"&customize_context_prompt={quote_plus(customize_context_prompt)}"
            )
        if full_profile_and_only_search_event is not None:
            params += f"&full_profile_and_only_search_event={'true' if full_profile_and_only_search_event else 'false'}"
        if fill_window_with_events is not None:
            params += f"&fill_window_with_events={'true' if fill_window_with_events else 'false'}"
        r = unpack_response(
            await self.project_client.client.get(
                f"/users/context/{self.user_id}{params}"
            )
        )
        return r.data["context"]
