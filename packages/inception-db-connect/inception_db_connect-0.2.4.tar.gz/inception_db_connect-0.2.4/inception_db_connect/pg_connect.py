from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from inception_db_connect.settings_db_connect import get_db_connect_setting
from inception_db_connect.helper import mask_url


# Retrieve settings
db_connect_setting = get_db_connect_setting()

if not db_connect_setting.postgres_url or not db_connect_setting.postgres_database:
    print(
        "❌ Environment misconfiguration: 'postgres_url' and 'postgres_database' must be set."
    )
    raise ValueError(
        "Both 'postgres_url' and 'postgres_database' environment variables must be set."
    )

SQLALCHEMY_DATABASE_URL = (
    f"{db_connect_setting.postgres_url}/{db_connect_setting.postgres_database}"
)

print(f"🐘 Connecting to PostgreSQL: {mask_url(SQLALCHEMY_DATABASE_URL)}")

# Set up engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

try:
    engine.connect()
    print("✅ Successfully connected to PostgreSQL!")
except Exception as e:
    print("❌ Failed to connect to PostgreSQL.")
    raise ConnectionError(f"PostgreSQL connection failed: {e}")


# Dependency (e.g., for FastAPI)
def get_pg_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_pg_db_on_demand():
    db = SessionLocal()
    return db
