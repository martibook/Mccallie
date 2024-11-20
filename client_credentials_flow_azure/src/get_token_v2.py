from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from msal import ConfidentialClientApplication
from cryptography.hazmat.primitives.serialization import pkcs12, Encoding, PrivateFormat, NoEncryption
from cryptography.hazmat.primitives.hashes import SHA1
from dotenv import load_dotenv
import base64
import os

# # Get an overview of the certificate from command line
# az keyvault certificate show --name <your-cert-name> --vault-name <your-key-vault-name>

# Load environment variables from .env file
load_dotenv()

# Configuration values from .env file
key_vault_url = os.getenv('KEY_VAULT_URL')
certificate_name = os.getenv('CERTIFICATE_NAME')
tenant_id = os.getenv('TENANT_ID')
client_id = os.getenv('CLIENT_ID')
scopes = os.getenv('SCOPES').split(',')


def get_client_credential():

    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=key_vault_url, credential=credential)
    secret = secret_client.get_secret(certificate_name)
    
    pfx_bytes = base64.b64decode(secret.value)
    p_key, cert, _ = pkcs12.load_key_and_certificates(
        pfx_bytes, None  # No password for the PFX
    )

    private_key = p_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    ).decode('utf-8')
    # print(f'Private Key:\n{private_key}\n')

    public_certificate = cert.public_bytes(encoding=Encoding.PEM).decode('utf-8')
    # print(f'Certificate:\n{public_certificate}\n')

    thumbprint = cert.fingerprint(SHA1()).hex()    
    # print(f'Thumbprint:\n{thumbprint}\n')

    return {
        "private_key": private_key,
        "public_certificate": public_certificate,
        "thumbprint": thumbprint,
    }


def get_access_token():

    client_credential = get_client_credential()
    app = ConfidentialClientApplication(
        client_id=client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        client_credential=client_credential
    )

    result = app.acquire_token_for_client(scopes=scopes)

    if "access_token" in result:
        return result["access_token"]
    else:
        print("Failed to acquire token:", result.get("error_description", "Unknown error"))
        return None


if __name__ == '__main__':
    print(get_access_token())