from memobase_server.models.blob import ChatBlob, DocBlob


def test_chat_blob_creation():
    blob = ChatBlob(
        messages=[{"role": "user", "content": "Hello, how are you?"}],
        fields={"name": "test_chat_blob"},
    )
    blob_data = blob.model_dump()
    assert blob_data["type"] == "chat"
    assert blob_data["messages"] == [{"role": "user", "content": "Hello, how are you?"}]
    assert blob_data["fields"] == {"name": "test_chat_blob"}


def test_doc_blob_creation():
    blob = DocBlob(
        content="This is a test document.",
        fields={"name": "test_doc_blob"},
    )
    blob_data = blob.model_dump()
    assert blob_data["type"] == "doc"
    assert blob_data["content"] == "This is a test document."
    assert blob_data["fields"] == {"name": "test_doc_blob"}
