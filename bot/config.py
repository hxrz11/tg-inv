import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "CHANGE_ME")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "tg_inv")

# Fields required to consider a service card complete
REQUIRED_FIELDS = ["type", "owner", "description"]
