from pymongo import MongoClient, errors
from inception_db_connect.settings_db_connect import get_db_connect_setting
from inception_db_connect.helper import mask_url

# Retrieve settings
db_connect_setting = get_db_connect_setting()

# Validate MongoDB settings
if not db_connect_setting.mongodb_database or not db_connect_setting.mongodb_url:
    print(
        "❌ Environment misconfiguration: 'mongodb_database' and 'mongodb_url' must be set."
    )
    raise ValueError(
        "Both 'mongodb_database' and 'mongodb_url' environment variables must be set."
    )

print(
    f"🔌 Connecting to MongoDB...\n🌐 URL: {mask_url(db_connect_setting.mongodb_url)}\n📁 Database: {db_connect_setting.mongodb_database}"
)
client = MongoClient(db_connect_setting.mongodb_url)

try:
    client.admin.command("ping")
    print("✅ Successfully connected to MongoDB!")
except errors.ServerSelectionTimeoutError as e:
    print("❌ Failed to connect to MongoDB.")
    raise ConnectionError(f"MongoDB connection failed: {e}")


# MongoDB dependency for FastAPI
def get_mongo_db():
    client = MongoClient(db_connect_setting.mongodb_url)
    db = client[db_connect_setting.mongodb_database]
    try:
        yield db
    finally:
        client.close()


# On-demand MongoDB access
def get_mongo_db_on_demand():
    client = MongoClient(db_connect_setting.mongodb_url)
    db = client[db_connect_setting.mongodb_database]
    return db
