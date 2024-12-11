import logging
import uuid

LOG = logging.getLogger("memobase")


def string_to_uuid(s: str, salt="memobase_client") -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, s + salt))
