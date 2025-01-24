import threading
from openai import OpenAI, AsyncOpenAI
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from openai._streaming import Stream
from ..core.entry import MemoBaseClient, User, ChatBlob
from ..core.user import UserProfile
from ..utils import string_to_uuid, LOG
from ..error import ServerError

PROMPT = """

--# ADDITIONAL INFO #--
Below is my information:
{user_profile}
Use the information to generate a more personalized response for me.
--# DONE #--"""


def openai_memory(
    openai_client: OpenAI | AsyncOpenAI, mb_client: MemoBaseClient
) -> OpenAI | AsyncOpenAI:
    if hasattr(openai_client, "_memobase_patched"):
        return openai_client

    openai_client._memobase_patched = True
    openai_client.get_profile = _get_profile(mb_client)
    openai_client.flush = _flush(mb_client)
    if isinstance(openai_client, OpenAI):
        openai_client.chat.completions.create = _sync_chat(openai_client, mb_client)
    elif isinstance(openai_client, AsyncOpenAI):
        raise ValueError(f"AsyncOpenAI is not supported yet")
    else:
        raise ValueError(f"Invalid openai_client type: {type(openai_client)}")
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


def add_message_to_user(messages: ChatBlob, user: User):
    try:
        r = user.insert(messages)
        LOG.debug(f"Insert {messages}")
    except ServerError as e:
        LOG.error(f"Failed to insert message: {e}")


def user_profile_insert(messages, u: User):
    profiles = u.profile()
    if not len(profiles):
        return messages
    user_profile_string = "\n".join(
        [f"- {p.topic}/{p.sub_topic}: {p.content}" for p in profiles]
    )
    sys_prompt = PROMPT.format(user_profile=user_profile_string)
    if messages[0]["role"] == "system":
        messages[0]["content"] += sys_prompt
    else:
        messages.insert(0, {"role": "system", "content": sys_prompt.strip()})
    return messages


def _sync_chat(client: OpenAI, mb_client: MemoBaseClient):
    _create_chat = client.chat.completions.create

    def sync_chat(*args, **kwargs) -> ChatCompletion | Stream[ChatCompletionChunk]:
        is_streaming = kwargs.get("stream", False)
        if kwargs.get("user_id", None) is None:
            kwargs.pop("user_id")
            if not is_streaming:
                return _create_chat(*args, **kwargs)
            else:
                return (r for r in _create_chat(*args, **kwargs))
        # TODO support streaming

        user_id = string_to_uuid(kwargs.pop("user_id"))
        user_query = kwargs["messages"][-1]
        if user_query["role"] != "user":
            LOG.warning(f"Last query is not user query: {user_query}")
            if not is_streaming:
                return _create_chat(*args, **kwargs)
            else:
                return (r for r in _create_chat(*args, **kwargs))

        u = mb_client.get_or_create_user(user_id)
        kwargs["messages"] = user_profile_insert(kwargs["messages"], u)
        response = _create_chat(*args, **kwargs)

        if is_streaming:

            def yield_response_and_log():
                total_response = ""
                r_role = None

                for r in response:
                    yield r
                    try:
                        r_string = r.choices[0].delta.content
                        r_role = r_role or r.choices[0].delta.role
                        total_response += r_string or ""
                    except Exception:
                        continue
                if not len(total_response):
                    return
                if r_role != "assistant":
                    LOG.warning(f"Last response is not assistant response: {r_role}")
                    return response

                messages = ChatBlob(
                    messages=[
                        {"role": "user", "content": user_query["content"]},
                        {"role": "assistant", "content": total_response},
                    ]
                )
                threading.Thread(target=add_message_to_user, args=(messages, u)).start()

            return yield_response_and_log()

        else:
            r_role = response.choices[0].message.role
            if r_role != "assistant":
                LOG.warning(f"Last response is not assistant response: {r_role}")
                return response
            r_string = response.choices[0].message.content
            messages = ChatBlob(
                messages=[
                    {"role": "user", "content": user_query["content"]},
                    {"role": "assistant", "content": r_string},
                ]
            )
            threading.Thread(target=add_message_to_user, args=(messages, u)).start()
            return response

    return sync_chat


# TODO support async openai
