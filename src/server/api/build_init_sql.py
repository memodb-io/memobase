import dotenv

dotenv.load_dotenv()
from sqlalchemy.schema import Table, CreateSchema, CreateIndex
from sqlalchemy.schema import CreateTable
import logging

logging.disable(logging.CRITICAL)
from memobase_server import __version__
from memobase_server.connectors import DB_ENGINE
from memobase_server.models.database import (
    User,
    GeneralBlob,
    BufferZone,
    UserProfile,
    user_profile_blobs,
)


print("--", f"Synced from backend {__version__}")
for db in [User, GeneralBlob, BufferZone, UserProfile, user_profile_blobs]:
    table_obj = db if isinstance(db, Table) else db.__table__
    print(str(CreateTable(table_obj).compile(DB_ENGINE)).strip() + ";")
