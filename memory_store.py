import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
USERS_FILE = DATA_DIR / "users.json"


def load_users():
    if not USERS_FILE.exists():
        save_users({})
    with USERS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_users(users):
    DATA_DIR.mkdir(exist_ok=True)
    with USERS_FILE.open("w", encoding="utf-8") as file:
        json.dump(users, file, indent=2)
