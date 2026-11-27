
import os
import json
import azure.functions as func
from azure.identity import ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="listblobs")
def listblobs(req: func.HttpRequest) -> func.HttpResponse:
    try:
        account_name = os.environ["STORAGE_ACCOUNT_NAME"]
        container_name = os.environ["CONTAINER_NAME"]
        client_id = os.environ["MANAGED_IDENTITY_CLIENT_ID"]

        account_url = f"https://{account_name}.blob.core.windows.net"
        credential = ManagedIdentityCredential(client_id=client_id)

        blob_service_client = BlobServiceClient(
            account_url=account_url,
            credential=credential
        )

        container_client = blob_service_client.get_container_client(container_name)
        blobs = [blob.name for blob in container_client.list_blobs()]

        return func.HttpResponse(
            json.dumps(
                {
                    "success": True,
                    "storage_account": account_name,
                    "container": container_name,
                    "blob_count": len(blobs),
                    "blobs": blobs,
                },
                ensure_ascii=False,
                indent=2,
            ),
            mimetype="application/json",
            status_code=200,
        )

    except Exception as e:
        return func.HttpResponse(
            json.dumps(
                {
                    "success": False,
                    "error": str(e),
                },
                ensure_ascii=False,
                indent=2,
            ),
            mimetype="application/json",
            status_code=500,
        )
