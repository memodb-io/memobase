from typing import Callable, Awaitable
from ...models.blob import BlobType, Blob
from ...models.utils import Promise
from . import chat
from . import summary

BlobProcessFunc = Callable[
    [str, str, list[Blob]],  # user_id, project_id, blobs
    Awaitable[Promise[None]],
]
BLOBS_PROCESS: dict[BlobType, BlobProcessFunc] = {
    BlobType.chat: chat.process_blobs,
    BlobType.summary: summary.process_blobs,
}
