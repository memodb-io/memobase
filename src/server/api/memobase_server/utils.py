from .env import ENCODER
from .models.blob import Blob, BlobType, ChatBlob, DocBlob
from typing import cast


def get_encoded_tokens(content: str):
    return ENCODER.encode(content)


def get_decoded_tokens(tokens: list[int]):
    return ENCODER.decode(tokens)


def get_blob_token_size(blob: Blob):
    match blob.type:
        case BlobType.chat:
            return len(
                get_encoded_tokens(
                    "\n".join([m.content for m in cast(ChatBlob, blob).messages])
                )
            )
        case BlobType.doc:
            return len(get_encoded_tokens(cast(DocBlob, blob).content))
        case _:
            raise ValueError(f"Unsupported Blob Type: {blob.type}")
