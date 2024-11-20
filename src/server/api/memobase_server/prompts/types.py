from dataclasses import dataclass, field
from typing import TypedDict, Optional

SubTopic = TypedDict("SubTopic", {"name": str, "description": Optional[str]})


@dataclass
class UserProfileTopic:
    topic: str
    sub_topics: list[SubTopic] = field(default_factory=list)

    def __post_init__(self):
        self.sub_topics = [
            {"name": st, "description": None} if isinstance(st, str) else st
            for st in self.sub_topics
        ]
        for st in self.sub_topics:
            assert isinstance(st["name"], str)
            assert isinstance(st["description"], (str, type(None)))
