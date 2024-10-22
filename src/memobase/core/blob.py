# Synced from memobase_server.models.blob on Tue Oct 22 14:54:18 CST 2024
from enum import StrEnum
from typing import Literal, Optional
from pydantic import BaseModel


class OpenAICompatibleMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class TranscriptStamp(BaseModel):
    content: str
    start_timestamp_in_seconds: float
    end_time_timestamp_in_seconds: Optional[float] = None
    speaker: Optional[str] = None


class BlobType(StrEnum):
    chat = "chat"
    doc = "doc"
    image = "image"
    code = "code"
    transcript = "transcript"


class Blob(BaseModel):
    type: BlobType
    fields: Optional[dict] = None

    def get_blob_data(self):
        return self.model_dump(exclude={"type", "fields"})


class ChatBlob(Blob):
    messages: list[OpenAICompatibleMessage]
    type: Literal[BlobType.chat] = BlobType.chat


class DocBlob(Blob):
    content: str
    type: Literal[BlobType.doc] = BlobType.doc


class CodeBlob(Blob):
    content: str
    language: Optional[str] = None
    type: Literal[BlobType.code] = BlobType.code


class ImageBlob(Blob):
    url: Optional[str] = None
    base64: Optional[str] = None
    type: Literal[BlobType.image] = BlobType.image


class TranscriptBlob(Blob):
    transcripts: list[TranscriptStamp]
    type: Literal[BlobType.transcript] = BlobType.transcript
