from openai import OpenAI, AsyncOpenAI
from ..core.entry import MemoBaseClient, User, ChatBlob
from ..core.user import UserProfile
from ..utils import string_to_uuid


def openai_memory(
    openai_client: OpenAI | AsyncOpenAI, mb_client: MemoBaseClient
) -> OpenAI | AsyncOpenAI:
    openai_client.get_profile = _get_profile(mb_client)
    openai_client.flush = _flush(mb_client)
    return openai_client


def _get_profile(mb_client: MemoBaseClient):
    def get_profile(u_string) -> list[UserProfile]:
        uid = string_to_uuid(u_string)
        return mb_client.get_user(uid, no_get=True).profile()

    return get_profile


def _flush(mb_client: MemoBaseClient):
    def flush(u_string) -> list[UserProfile]:
        uid = string_to_uuid(u_string)
        return mb_client.get_user(uid, no_get=True).flush()

    return flush
