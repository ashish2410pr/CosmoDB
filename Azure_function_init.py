import datetime
import json
import azure.functions as func
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient

# Configuration (Use env vars in production)
COSMOS_URI = "<COSMOS_DB_URI>"
COSMOS_KEY = "<COSMOS_DB_KEY>"
DATABASE_NAME = "<DATABASE_NAME>"
CONTAINER_NAME = "<CONTAINER_NAME>"

BLOB_CONN_STR = "<BLOB_CONNECTION_STRING>"
BLOB_CONTAINER = "billing-archive"

def main(documents: func.DocumentList) -> None:
    if not documents:
        return

    cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=90)

    cosmos_client = CosmosClient(COSMOS_URI, COSMOS_KEY)
    container_client = cosmos_client.get_database_client(DATABASE_NAME).get_container_client(CONTAINER_NAME)

    blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONN_STR)
    blob_container_client = blob_service_client.get_container_client(BLOB_CONTAINER)

    for doc in documents:
        try:
            record_ts = datetime.datetime.fromisoformat(doc['timestamp'])
            if record_ts < cutoff_date:
                record_id = doc['id']
                year = record_ts.strftime("%Y")
                month = record_ts.strftime("%m")
                blob_path = f"billing/{year}/{month}/{record_id}.json"

                blob_client = blob_container_client.get_blob_client(blob_path)
                blob_client.upload_blob(json.dumps(doc), overwrite=True)

                container_client.delete_item(item=record_id, partition_key=doc['partitionKey'])
                print(f"Archived record: {record_id}")

        except Exception as e:
            print(f"[ERROR] Failed to archive record {doc.get('id')}: {e}")
