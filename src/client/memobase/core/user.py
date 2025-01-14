from dataclasses import dataclass
from pydantic import BaseModel, UUID4, UUID5
from typing import Optional
from datetime import datetime


@dataclass
class UserProfile:
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
            updated_at=self.updated_at,
            topic=self.attributes.get("topic", "NONE"),
            sub_topic=self.attributes.get("sub_topic", "NONE"),
            content=self.content,
        )
