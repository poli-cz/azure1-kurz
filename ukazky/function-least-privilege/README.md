
Azure Least Privilege Demo (Managed Identity + Blob Storage)

This demo shows how an Azure Function can access a Blob Storage container
using a User Assigned Managed Identity and RBAC instead of secrets.

FILES
-----
function_app.py      - Azure Function code
requirements.txt     - Python dependencies

STEPS
-----

1. Create resources
   - Storage Account
   - Blob container (e.g. demo-data)
   - Upload a few files
   - User Assigned Managed Identity
   - Function App (Python)

2. Attach identity to Function App
   Function App → Identity → User assigned → Add → select your identity

3. Grant RBAC role
   Storage Account → Access control (IAM)
   Role: Storage Blob Data Reader
   Assign to: your Managed Identity

4. Configure environment variables in Function App
   Settings → Environment variables

   STORAGE_ACCOUNT_NAME = your storage account
   CONTAINER_NAME = your blob container
   MANAGED_IDENTITY_CLIENT_ID = client id of the managed identity

5. Deploy the files
   Upload function_app.py and requirements.txt

6. Call the function

   https://YOUR_FUNCTION_APP.azurewebsites.net/api/listblobs

EXPECTED RESULT
---------------

JSON response containing a list of blobs in the container.

If RBAC role is missing you should receive an authorization error.
After adding the role the request should succeed.

This demonstrates the principle of least privilege using Azure Managed Identity.
