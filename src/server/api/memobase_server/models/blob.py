from enum import StrEnum
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel


class OpenAICompatibleMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    alias: Optional[str] = None
    created_at: Optional[str] = None


class TranscriptStamp(BaseModel):
    content: str
    start_timestamp_in_seconds: float
    end_time_timestamp_in_seconds: Optional[float] = None
    speaker: Optional[str] = None


class BlobType(StrEnum):
    chat = "chat"
    summary = "summary"
    doc = "doc"
    image = "image"
    code = "code"
    transcript = "transcript"


class Blob(BaseModel):
    type: BlobType
    fields: Optional[dict] = None
    created_at: Optional[datetime] = None

    def get_blob_data(self):
        return self.model_dump(exclude={"type", "fields", "created_at"})

    def to_request(self):
        return {
            "blob_type": self.type,
            "fields": self.fields,
            "blob_data": self.get_blob_data(),
        }


class ChatBlob(Blob):
    messages: list[OpenAICompatibleMessage]
    type: Literal[BlobType.chat] = BlobType.chat


class SummaryBlob(Blob):
    summary: str
    type: Literal[BlobType.summary] = BlobType.summary


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


class BlobData(BaseModel):
    blob_type: BlobType
    blob_data: dict  # messages/doc/images...
    fields: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_blob(self) -> Blob:
        if self.blob_type == BlobType.chat:
            return ChatBlob(
                **self.blob_data, fields=self.fields, created_at=self.created_at
            )
        elif self.blob_type == BlobType.summary:
            return SummaryBlob(
                **self.blob_data, fields=self.fields, created_at=self.created_at
            )
        elif self.blob_type == BlobType.doc:
            return DocBlob(
                **self.blob_data, fields=self.fields, created_at=self.created_at
            )
        elif self.blob_type == BlobType.image:
            raise NotImplementedError("ImageBlob not implemented yet.")
        elif self.blob_type == BlobType.transcript:
            raise NotImplementedError("TranscriptBlob not implemented yet.")
