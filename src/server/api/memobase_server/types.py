from pydantic import BaseModel, field_validator
from dataclasses import dataclass, field
from typing import Optional


def attribute_unify(attr: str):
    return attr.lower().strip().replace(" ", "_")


class SubTopic(BaseModel):
    name: str
    description: Optional[str] = None
    update_description: Optional[str] = None
    validate_value: Optional[bool] = None

    @field_validator("name")
    def validate_name(cls, v):
        return attribute_unify(v)

    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key, default=None):
        return getattr(self, key, default)


@dataclass
class EventTag:
    name: str
    description: Optional[str] = None

    def __post_init__(self):
        self.name = attribute_unify(self.name)
        self.description = self.description or ""


@dataclass
class UserProfileTopic:
    topic: str
    description: Optional[str] = None
    sub_topics: list[SubTopic] = field(default_factory=list)

    def __post_init__(self):
        self.topic = attribute_unify(self.topic)
        self.sub_topics = [
            SubTopic(**{"name": st}) if isinstance(st, str) else SubTopic(**st)
            for st in self.sub_topics
        ]
