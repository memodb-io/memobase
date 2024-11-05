from .env import ENCODER
from .models.blob import Blob, BlobType, ChatBlob, DocBlob
from typing import cast


def get_encoded_tokens(content: str):
    return ENCODER.encode(content)


def get_decoded_tokens(tokens: list[int]):
    return ENCODER.decode(tokens)


def pack_blob_from_db(blob_data: dict, blob_type: BlobType) -> Blob:
    match blob_type:
        case BlobType.chat:
            return ChatBlob(**blob_data)
        case BlobType.doc:
            return DocBlob(**blob_data)
        case _:
            raise ValueError(f"Unsupported Blob Type: {blob_type}")


def get_blob_str(blob: Blob):
    match blob.type:
        case BlobType.chat:
            return "\n".join(
                [f"{m.role}: {m.content}" for m in cast(ChatBlob, blob).messages]
            )
        case BlobType.doc:
            return cast(DocBlob, blob).content
        case _:
            raise ValueError(f"Unsupported Blob Type: {blob.type}")


def get_blob_token_size(blob: Blob):
    return len(get_encoded_tokens(get_blob_str(blob)))
