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
)


print("--", f"Synced from backend {__version__}")
for db in [User, GeneralBlob, BufferZone, UserProfile]:
    table_obj = db if isinstance(db, Table) else db.__table__
    # Print table creation
    print(str(CreateTable(table_obj).compile(DB_ENGINE)).strip() + ";")
    # Print indexes
    for index in table_obj.indexes:
        print(str(CreateIndex(index).compile(DB_ENGINE)).strip() + ";")
