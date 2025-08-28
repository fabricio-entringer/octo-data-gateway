

from pathlib import Path
from tinydb import TinyDB

from app.database.config import DATABASE_DIR
from .models import UserUsage


data_dir = Path(DATABASE_DIR)
data_dir.mkdir(exist_ok=True)

db = TinyDB(data_dir / "edg_usage_db.json")
user_usage = db.table("user_usage")

def log_user_usage(usage: UserUsage) -> None:
    user_usage.insert(usage.model_dump(mode="json"))