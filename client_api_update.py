from fastapi import FastAPI, HTTPException
import json
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient, exceptions

app = FastAPI()

# Configure clients
COSMOS_URI = "<COSMOS_DB_URI>"
COSMOS_KEY = "<COSMOS_DB_KEY>"
DATABASE_NAME = "<DATABASE_NAME>"
CONTAINER_NAME = "<CONTAINER_NAME>"
BLOB_CONN_STR = "<BLOB_CONNECTION_STRING>"

cosmos_client = CosmosClient(COSMOS_URI, COSMOS_KEY)
cosmos_container = cosmos_client.get_database_client(DATABASE_NAME).get_container_client(CONTAINER_NAME)
blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONN_STR)

def guess_year_month_from_id(record_id):
    # You can derive this from metadata in Cosmos or use other logic
    return "2024", "01"

@app.get("/billing/{record_id}")
def get_billing_record(record_id: str, partition_key: str):
    try:
        record = cosmos_container.read_item(item=record_id, partition_key=partition_key)
        return record
    except exceptions.CosmosResourceNotFoundError:
        year, month = guess_year_month_from_id(record_id)
        blob_path = f"billing/{year}/{month}/{record_id}.json"
        try:
            blob_client = blob_service_client.get_blob_client(container="billing-archive", blob=blob_path)
            blob_data = blob_client.download_blob().readall()
            return json.loads(blob_data)
        except Exception:
            raise HTTPException(status_code=404, detail="Record not found")
