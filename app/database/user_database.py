from pathlib import Path
import uuid
from tinydb import TinyDB, Query
from .models import User, Scopes

data_dir = Path("./data")
data_dir.mkdir(exist_ok=True)

db = TinyDB("./data/edg_db.json")
user_table = db.table("users")

def add_user(user: User) -> User:
    user.user_id = str(uuid.uuid4())
    user.api_key = str(uuid.uuid4())
    user_table.insert(user.model_dump())
    return user

def get_user(user_id: str) -> User | None:
    user_data = user_table.get(Query().user_id == user_id)
    return User(**user_data) if user_data else None

def update_user(user_id: str, user: User):
    user_table.update(user.model_dump(), Query().user_id == user_id)

def delete_user(user_id: str):
    user_table.remove(Query().user_id == user_id)

def get_all_users() -> list[User]:
    users_data = user_table.all()
    return [User(**user_data) for user_data in users_data]

def get_user_by_api_key(api_key: str) -> User | None:
    user_data = user_table.get(Query().api_key == api_key)
    return User(**user_data) if user_data else None

def get_user_by_name(name: str) -> User | None:
    user_data = user_table.get(Query().name == name)
    return User(**user_data) if user_data else None

def get_user_by_email(email: str) -> User | None:
    user_data = user_table.get(Query().email == email)
    return User(**user_data) if user_data else None


def ensure_default_user_exists() -> User | None:
    """
    Ensure that at least one user exists in the database.
    If the table is empty, create a default master user.
    Returns the default user if created, None if users already exist.
    """
    
    if len(user_table) == 0:
        default_user = User(
            name="Default Master User",
            description="This is a default master user created for the application.",
            scopes=[Scopes.MASTER],
        )
        add_user(default_user)
        print(f"\033[92mCreated default user: {default_user.name} (ID: {default_user.user_id})\033[0m")
        print(f"\033[91mAPI Key: {default_user.api_key}\033[0m")
        return default_user
    return None

# Initialize default user when the module is imported
ensure_default_user_exists()
