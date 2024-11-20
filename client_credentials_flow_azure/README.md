# get_token_v2.py

Assuming you have a certificate(CERTIFICATE_NAME) stored in Azure Key Vault(KEY_VAULT_URL), which acts as your credentials.

This tool gets an access token(denoted by TENANT_ID and SCOPES) on behalf of an App(CLIENT_ID, actually an application ID) using the above-mentioned credentials.

Once the access token fetched, your App is able to call services allowed in the SCOPES



# get_token_v1.py

A earlier version of the implementation.