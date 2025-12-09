from datetime import datetime
from enum import IntEnum
from typing import Optional, Literal
from pydantic import BaseModel, UUID4, UUID5, Field
from .blob import BlobData, OpenAICompatibleMessage
from .claim import ClaimData
from .action import ActionData

UUID = UUID4 | UUID5


class CODE(IntEnum):
    # Success
    SUCCESS = 0

    # Client-side errors (4xx)
    BAD_REQUEST = 400  # The request could not be understood by the server due to malformed syntax.
    UNAUTHORIZED = 401  # The request requires user authentication.
    FORBIDDEN = 403  # The server understood the request, but is refusing to fulfill it.
    NOT_FOUND = 404  # The server has not found anything matching the Request-URI.
    METHOD_NOT_ALLOWED = 405  # The method specified in the Request-Line is not allowed for the resource identified by the Request-URI.
    CONFLICT = 409  # The request could not be completed due to a conflict with the current state of the resource.
    UNPROCESSABLE_ENTITY = 422  # The server understands the content type of the request entity, and the syntax is correct, but it was unable to process the contained instructions.

    # Server-side errors (5xx)
    INTERNAL_SERVER_ERROR = 500  # The server encountered an unexpected condition which prevented it from fulfilling the request.
    NOT_IMPLEMENTED = 501  # The server does not support the functionality required to fulfill the request.
    BAD_GATEWAY = 502  # The server, while acting as a gateway or proxy, received an invalid response from the upstream server.
    SERVICE_UNAVAILABLE = 503  # The server is currently unable to handle the request due to a temporary overloading or maintenance of the server.
    GATEWAY_TIMEOUT = 504  # The server, while acting as a gateway or proxy, did not receive a timely response from the upstream server.
    SERVER_PARSE_ERROR = 520  # The server could not parse the request.


class AIUserProfile(BaseModel):
    topic: str = Field(..., description="The main topic of the user profile")
    sub_topic: str = Field(..., description="The sub-topic of the user profile")
    memo: str = Field(..., description="The memo content of the user profile")


class AIUserProfiles(BaseModel):
    facts: list[AIUserProfile] = Field(..., description="List of user profile facts")


# Return data format
class IdData(BaseModel):
    id: UUID = Field(..., description="The UUID identifier")


class IdsData(BaseModel):
    ids: list[UUID] = Field(..., description="List of UUID identifiers")


class ChatModalResponse(BaseModel):
    event_id: Optional[UUID] = Field(..., description="The event's unique identifier")
    add_profiles: Optional[list[UUID]] = Field(
        ..., description="List of added profiles' ids"
    )
    update_profiles: Optional[list[UUID]] = Field(
        ..., description="List of updated profiles' ids"
    )
    delete_profiles: Optional[list[UUID]] = Field(
        ..., description="List of deleted profiles' ids"
    )


class ProfileAttributes(BaseModel):
    topic: str = Field(..., description="The topic of the profile")
    sub_topic: str = Field(..., description="The sub-topic of the profile")


class ProfileData(BaseModel):
    id: UUID = Field(..., description="The profile's unique identifier")
    content: str = Field(..., description="User profile content value")
    created_at: datetime = Field(
        None, description="Timestamp when the profile was created"
    )
    updated_at: datetime = Field(
        None, description="Timestamp when the profile was last updated"
    )
    attributes: Optional[dict] = Field(
        None,
        description="User profile attributes in JSON, containing 'topic', 'sub_topic'",
    )


class ProfileDelta(BaseModel):
    content: str = Field(..., description="The profile content")
    attributes: Optional[dict] = Field(
        ...,
        description="User profile attributes in JSON, containing 'topic', 'sub_topic'",
    )


class EventTag(BaseModel):
    tag: str = Field(..., description="The event tag")
    value: str = Field(..., description="The event tag value")


class EventGistData(BaseModel):
    content: str = Field(..., description="The event gist content")


class EventData(BaseModel):
    profile_delta: Optional[list[ProfileDelta]] = Field(
        None, description="List of profile data"
    )
    event_tip: Optional[str] = Field(None, description="Event tip")
    event_tags: Optional[list[EventTag]] = Field(None, description="List of event tags")


class UserEventGistData(BaseModel):
    id: UUID = Field(..., description="The event gist's unique identifier")
    gist_data: EventGistData = Field(None, description="User event gist data")
    created_at: datetime = Field(
        None, description="Timestamp when the event gist was created"
    )
    updated_at: datetime = Field(
        None, description="Timestamp when the event gist was last updated"
    )
    similarity: Optional[float] = Field(None, description="Similarity score")


class UserEventData(BaseModel):
    id: UUID = Field(..., description="The event's unique identifier")
    event_data: EventData = Field(None, description="User event data in JSON")
    created_at: datetime = Field(
        None, description="Timestamp when the event was created"
    )
    updated_at: datetime = Field(
        None, description="Timestamp when the event was last updated"
    )
    similarity: Optional[float] = Field(None, description="Similarity score")


class ContextData(BaseModel):
    context: str = Field(..., description="Context string")


class UserData(BaseModel):
    data: Optional[dict] = Field(None, description="User additional data in JSON")
    id: Optional[UUID] = Field(None, description="User ID in UUIDv4/5")
    created_at: Optional[datetime] = Field(
        None, description="Timestamp when the user was created"
    )
    updated_at: Optional[datetime] = Field(
        None, description="Timestamp when the user was last updated"
    )


class UserProfilesData(BaseModel):
    profiles: list[ProfileData] = Field(..., description="List of user profiles")


class UserEventsData(BaseModel):
    events: list[UserEventData] = Field(..., description="List of user events")
    gists: list[UserEventGistData] = Field(
        default_factory=list, description="List of user event gists"
    )


class UserEventGistsData(BaseModel):
    gists: list[UserEventGistData] = Field(..., description="List of user event gists")
    events: list[UserEventData] = Field(
        default_factory=list, description="List of user events"
    )


class StrIntData(BaseModel):
    data: dict[str, int] = Field(..., description="String to int mapping")


class MessageData(BaseModel):
    data: list[OpenAICompatibleMessage] = Field(..., description="List of messages")


class QueryData(BaseModel):
    claims: list[ClaimData] = Field(..., description="List of claim data")
    actions: list[ActionData] = Field(..., description="List of action data")


class ProfileConfigData(BaseModel):
    profile_config: str | None = Field(..., description="Profile config string")


class BillingData(BaseModel):
    token_left: Optional[int] = Field(None, description="Total token left")

    next_refill_at: Optional[datetime] = Field(None, description="Next refill time")
    project_token_cost_month: int = Field(
        ..., description="Token cost of this project for this month"
    )


class UserStatusData(BaseModel):
    id: UUID = Field(..., description="User status id")

    type: str = Field(..., description="User status type")
    attributes: dict = Field(..., description="User status attributes")

    created_at: Optional[datetime] = Field(
        None, description="Timestamp when the user was created"
    )
    updated_at: Optional[datetime] = Field(
        None, description="Timestamp when the user was last updated"
    )


class UserStatusesData(BaseModel):
    statuses: list[UserStatusData] = Field(..., description="List of user statuses")


class ProactiveTopicData(BaseModel):
    action: Literal["new_topic", "continue"] = Field(
        ..., description="The action to take"
    )
    topic_prompt: Optional[str] = Field(
        None,
        description="The topic prompt, insert it to your latest user message or system prompt",
    )


class ProactiveTopicRequest(BaseModel):
    messages: list[OpenAICompatibleMessage] = Field(
        ..., description="The latest messages between user/assistant"
    )
    agent_context: Optional[str] = Field(
        None, description="The agent's roleplay prompt"
    )


class UserContextImport(BaseModel):
    context: str = Field(
        ..., description="The user context you want to import to Memobase"
    )


class ProjectUsersData(BaseModel):
    users: list = Field(..., description="The user list")
    count: int = Field(0, description="The user count")


class DailyUsage(BaseModel):
    date: str = Field(..., description="The date")
    total_insert: int = Field(0, description="The total insert")
    total_success_insert: int = Field(0, description="The total update")
    total_input_token: int = Field(0, description="The total input token")
    total_output_token: int = Field(0, description="The total output token")


# API response format
class BaseResponse(BaseModel):
    data: Optional[dict] = Field(None, description="Response data payload")
    errno: CODE = Field(CODE.SUCCESS, description="Error code, 0 means success")
    errmsg: str = Field("", description="Error message, empty when success")


class IdResponse(BaseResponse):
    data: Optional[IdData] = Field(None, description="Response containing a single ID")


class IdsResponse(BaseResponse):
    data: Optional[IdsData] = Field(
        None, description="Response containing multiple IDs"
    )


class ProfileConfigDataResponse(BaseResponse):
    data: Optional[ProfileConfigData] = Field(
        None, description="Response containing profile config data"
    )


class UserDataResponse(BaseResponse):
    data: Optional[UserData] = Field(None, description="Response containing user data")


class BlobDataResponse(BaseResponse):
    data: Optional[BlobData] = Field(None, description="Response containing blob data")


class QueryDataResponse(BaseResponse):
    data: Optional[QueryData] = Field(
        None, description="Response containing query results"
    )


class UserProfileResponse(BaseResponse):
    data: Optional[UserProfilesData] = Field(
        None, description="Response containing user profiles"
    )


class UserEventsDataResponse(BaseResponse):
    data: Optional[UserEventsData] = Field(
        None, description="Response containing user events"
    )


class UserEventGistsDataResponse(BaseResponse):
    data: Optional[UserEventGistsData] = Field(
        None, description="Response containing user event gists"
    )


class UserContextDataResponse(BaseResponse):
    data: Optional[ContextData] = Field(
        None, description="Response containing user context"
    )


class BillingResponse(BaseResponse):
    data: Optional[BillingData] = Field(
        None, description="Response containing token left"
    )


class ChatModalAPIResponse(BaseResponse):
    data: Optional[list[ChatModalResponse]] = Field(
        None, description="Response containing chat modal data"
    )


class BlobInsertData(IdData):
    chat_results: Optional[list[ChatModalResponse]] = Field(
        None, description="List of chat modal data"
    )


class BlobInsertResponse(BaseResponse):
    data: Optional[BlobInsertData] = Field(
        None, description="Response containing blob insert data"
    )


class ProactiveTopicResponse(BaseResponse):
    data: Optional[ProactiveTopicData] = Field(
        None, description="Response containing proactive topic data"
    )


class ProjectUsersDataResponse(BaseResponse):
    data: Optional[ProjectUsersData] = Field(
        None, description="Response containing the users"
    )


class UsageResponse(BaseResponse):
    data: Optional[list[DailyUsage]] = Field(
        None, description="Response containing the daily usage"
    )
