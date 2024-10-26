import dotenv

dotenv.load_dotenv()
from sqlalchemy.schema import CreateTable
from memobase_server import __version__
from memobase_server.connectors import DB_ENGINE
from memobase_server.models.database import User, GeneralBlob, BufferZone


print("--", f"Synced from backend {__version__}")
for db in [User, GeneralBlob, BufferZone]:
    print(str(CreateTable(db.__table__).compile(DB_ENGINE)).strip() + ";")
