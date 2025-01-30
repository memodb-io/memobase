from datetime import datetime
from enum import IntEnum
from typing import Optional
from pydantic import BaseModel, UUID4, UUID5, Field
from .blob import BlobData
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


class QueryData(BaseModel):
    claims: list[ClaimData] = Field(..., description="List of claim data")
    actions: list[ActionData] = Field(..., description="List of action data")


# API response format
class BaseResponse(BaseModel):
    data: Optional[dict] = Field(None, description="Response data payload")
    errno: CODE = Field(CODE.SUCCESS, description="Error code, 0 means success")
    errmsg: str = Field("", description="Error message, empty when success")


class IdResponse(BaseResponse):
    data: Optional[IdData] = Field(None, description="Response containing a single ID")


class SecretResponse(BaseResponse):
    data: Optional[str] = Field(None, description="Response containing a secret key")


class IdsResponse(BaseResponse):
    data: Optional[IdsData] = Field(
        None, description="Response containing multiple IDs"
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
