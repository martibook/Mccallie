from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient
from azure.keyvault.secrets import SecretClient
from msal import ConfidentialClientApplication
from cryptography.hazmat.primitives.serialization import pkcs12, Encoding, PrivateFormat, NoEncryption
from dotenv import load_dotenv
import base64
import os


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
    certificate_client = CertificateClient(vault_url=key_vault_url, credential=credential)
    secret_client = SecretClient(vault_url=key_vault_url, credential=credential)

    certificate = certificate_client.get_certificate(certificate_name)
    thumbprint = certificate.properties.x509_thumbprint.hex()
    # print(f'Thumbprint:\n{thumbprint}\n')

    # The public certificate is included in the 'cer' property, which is a byte array
    public_certificate_bytes = certificate.cer

    public_certificate_pem = f"-----BEGIN CERTIFICATE-----\n"
    public_certificate_pem += base64.b64encode(public_certificate_bytes).decode('utf-8')
    public_certificate_pem += "\n-----END CERTIFICATE-----"
    # print(f'Certificate:\n{public_certificate_pem}\n')

    secret = secret_client.get_secret(certificate_name)
    pfx_bytes = base64.b64decode(secret.value)

    private_key, _, _ = pkcs12.load_key_and_certificates(
        pfx_bytes, None  # No password for the PFX
    )

    private_key_pem = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )
    # print(f'Private Key PEM:\n{private_key_pem}\n')

    return {
        "private_key": private_key_pem.decode("utf-8"),
        "public_certificate": public_certificate_pem,
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