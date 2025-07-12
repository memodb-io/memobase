from dataclasses import dataclass
from pydantic import BaseModel, UUID4, UUID5, Field
from typing import Optional
from datetime import datetime


@dataclass
class UserProfile:
    id: str
    created_at: datetime
    updated_at: datetime
    topic: str
    sub_topic: str
    content: str

    @property
    def describe(self) -> str:
        return f"{self.topic}: {self.sub_topic} - {self.content}"


class UserProfileData(BaseModel):
    id: UUID4 | UUID5
    content: str
    attributes: dict
    created_at: datetime
    updated_at: datetime

    def to_ds(self):
        return UserProfile(
            id=self.id,
            content=self.content,
            topic=self.attributes.get("topic", "NONE"),
            sub_topic=self.attributes.get("sub_topic", "NONE"),
            created_at=self.created_at,
            updated_at=self.updated_at,
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


class EventData(BaseModel):
    profile_delta: list[ProfileDelta] = Field(..., description="List of profile data")
    event_tip: Optional[str] = Field(None, description="Event tip")
    event_tags: Optional[list[EventTag]] = Field(None, description="List of event tags")


class EventGistData(BaseModel):
    content: str = Field(..., description="The event gist content")


class UserEventData(BaseModel):
    id: UUID4 | UUID5 = Field(..., description="The event's unique identifier")
    event_data: Optional[EventData] = Field(None, description="User event data in JSON")
    created_at: datetime = Field(
        None, description="Timestamp when the event was created"
    )
    updated_at: datetime = Field(
        None, description="Timestamp when the event was last updated"
    )
    similarity: Optional[float] = Field(None, description="Similarity score")


class UserEventGistData(BaseModel):
    id: UUID4 | UUID5 = Field(..., description="The event gist's unique identifier")
    gist_data: EventGistData = Field(None, description="User event gist data")
    created_at: datetime = Field(
        None, description="Timestamp when the event gist was created"
    )
    updated_at: datetime = Field(
        None, description="Timestamp when the event gist was last updated"
    )
    similarity: Optional[float] = Field(None, description="Similarity score")
