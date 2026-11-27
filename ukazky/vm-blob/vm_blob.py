from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# Change these values
storage_account_name = "mystorageaccount"
container_name = "demo-data"

account_url = f"https://{storage_account_name}.blob.core.windows.net"

# On Azure VM, DefaultAzureCredential will use Managed Identity automatically
credential = DefaultAzureCredential()

blob_service_client = BlobServiceClient(
    account_url=account_url,
    credential=credential
)

container_client = blob_service_client.get_container_client(container_name)

print(f"Blobs in container '{container_name}':")
for blob in container_client.list_blobs():
    print("-", blob.name)
