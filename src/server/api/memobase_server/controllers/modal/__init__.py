from typing import Callable, Awaitable
from ...models.blob import BlobType, Blob
from ...models.utils import Promise
from . import chat

BlobProcessFunc = Callable[
    [str, list[str], list[Blob]],  # user_id, blob_ids, blobs
    Awaitable[Promise[None]],
]
BLOBS_PROCESS: dict[BlobType, BlobProcessFunc] = {BlobType.chat: chat.process_blobs}
