import boto3
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch
from opensearchpy import OpenSearch, RequestsHttpConnection
from inception_db_connect.settings_db_connect import get_db_connect_setting
from inception_db_connect.helper import mask_url

# Get settings
db_connect_setting = get_db_connect_setting()
print(
    f"📡 Connecting to Elasticsearch at: {mask_url(db_connect_setting.elasticsearch_url)}"
)


def es_connect():
    # Connect to ES
    if db_connect_setting.elasticsearch_provider == "aws":
        # Get AWS credentials
        # credentials = boto3.Session().get_credentials()
        credentials = boto3.Session().get_credentials().get_frozen_credentials()
        awsauth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            db_connect_setting.aws_region,
            db_connect_setting.elasticsearch_service,
            session_token=credentials.token,
        )

        es = OpenSearch(
            hosts=[
                {
                    "host": db_connect_setting.elasticsearch_host.split("//")[1],
                    "port": db_connect_setting.elasticsearch_port,
                }
            ],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=db_connect_setting.elasticsearch_verify_certs,
            connection_class=RequestsHttpConnection,
        )
    elif db_connect_setting.elasticsearch_provider == "self-hosted":
        es = Elasticsearch(
            [
                f"{db_connect_setting.elasticsearch_host}:{db_connect_setting.elasticsearch_port}"
            ],
            verify_certs=db_connect_setting.elasticsearch_verify_certs,
        )
    return es


# ✅ Confirm connection
es = es_connect()
if es.ping():
    print("✅ Successfully connected to Elasticsearch!")
else:
    print("❌ Failed to connect to Elasticsearch.")
    raise ConnectionError("Could not connect to Elasticsearch.")


def get_es_client():
    es_client = es_connect()
    try:
        yield es_client
    finally:
        es_client.close()


def get_es_client_on_demand():
    return es


async def index_document(index_name: str, document_id: str, body: dict):
    response = es.index(index=index_name, id=document_id, document=body)
    print(f"✅ Successfully indexed document into Elasticsearch: {document_id}")
    return response


async def search_es_documents(index_name: str, query: dict):
    response = es.search(index=index_name, body=query)
    print(f"✅ Successfully searched Elasticsearch: {response}")
    return response
