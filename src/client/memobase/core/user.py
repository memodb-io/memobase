from dataclasses import dataclass
from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime


@dataclass
class UserProfile:
    updated_at: datetime
    topic: str
    sub_topic: str
    content: str
    related_blob_ids: list[str]

    @property
    def describe(self) -> str:
        return f"{self.topic}: {self.sub_topic} - {self.content}"


class UserProfileData(BaseModel):
    id: UUID4
    content: str
    attributes: dict
    related_blobs: list[str]
    created_at: datetime
    updated_at: datetime

    def to_ds(self):
        return UserProfile(
            updated_at=self.updated_at,
            topic=self.attributes.get("topic", "NONE"),
            sub_topic=self.attributes.get("sub_topic", "NONE"),
            content=self.content,
            related_blob_ids=self.related_blobs,
        )
