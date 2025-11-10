import os
import time
import socket
from dotenv import load_dotenv
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # AppAuth Settings
    application_name: str = ""
    application_version: str = ""
    # Connection Settings
    mongodb_database: str = ""
    mongodb_url: str = ""
    aws_region: str = "eu-west-1"
    elasticsearch_service: str = "es"
    elasticsearch_host: str = ""
    elasticsearch_port: int = 443
    elasticsearch_verify_certs: bool = True
    elasticsearch_provider: str = ("self-hosted",)  # aws, azure, gcp, self-hosted
    postgres_url: str = ""
    postgres_database: str = ""
    hostname: str = socket.gethostname()
    ip_address: str = socket.gethostbyname(hostname)
    env_file: str = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(dotenv_path=env_file)
    model_config = SettingsConfigDict(env_file=env_file)


@lru_cache(maxsize=1)
def get_db_connect_setting() -> Settings:
    return Settings()


def init_database_connection(
    application_name: str,
    application_version: str,
    mongodb_url: str = "",
    mongodb_database: str = "",
    postgres_url: str = "",
    postgres_database: str = "",
    aws_region: str = "eu-west-1",
    elasticsearch_service: str = "es",
    elasticsearch_host: str = "",
    elasticsearch_port: int = 443,
    elasticsearch_verify_certs: bool = False,
    elasticsearch_provider: str = "self-hosted",  # aws, azure, gcp, self-hosted
):

    env_file = os.path.join(os.path.dirname(__file__), ".env")
    with open(env_file, "w") as f:
        f.write(f'application_name="{application_name}"\n')
        f.write(f'application_version="{application_version}"\n')
        f.write(f'elasticsearch_host="{elasticsearch_host}"\n')
        f.write(f'elasticsearch_port="{elasticsearch_port}"\n')
        f.write(f'elasticsearch_verify_certs="{elasticsearch_verify_certs}"\n')
        f.write(f'mongodb_url="{mongodb_url}"\n')
        f.write(f'mongodb_database="{mongodb_database}"\n')
        f.write(f'postgres_url="{postgres_url}"\n')
        f.write(f'postgres_database="{postgres_database}"\n')
        f.write(f'aws_region="{aws_region}"\n')
        f.write(f'elasticsearch_service="{elasticsearch_service}"\n')
        f.write(f'elasticsearch_provider="{elasticsearch_provider}"\n')
    time.sleep(3)
    os.chmod(env_file, 0o777)
    # load the settings
    # db_connect_settings = get_db_connect_setting().model_dump()
    # print("DB Connect settings: ", db_connect_settings)


if __name__ == "__main__":
    init_database_connection(
        application_name="test_application",
        application_version="1.0.0",
        mongodb_url="mongodb://localhost:27017",
        mongodb_database="test_database",
        postgres_url="postgresql://postgres:postgres@localhost:5432/postgres",
        postgres_database="postgres",
        aws_region="eu-west-1",
        elasticsearch_service="es",
        elasticsearch_provider="aws",
        elasticsearch_host="search-your-domain-name.eu-west-1.es.amazonaws.com",
        elasticsearch_port=443,
        elasticsearch_verify_certs=True,
    )
