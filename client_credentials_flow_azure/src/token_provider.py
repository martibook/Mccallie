from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from msal import ConfidentialClientApplication
from cryptography.hazmat.primitives.serialization import pkcs12, Encoding, PrivateFormat, NoEncryption
from cryptography.hazmat.primitives.hashes import SHA1
from dotenv import load_dotenv
import base64
import os

load_dotenv()

class TokenProvider:
    
    def __init__(self) -> None:
        self.key_vault_url = os.getenv('KEY_VAULT_URL')
        self.certificate_name = os.getenv('CERTIFICATE_NAME')
        self.tenant_id = os.getenv('TENANT_ID')
        self.client_id = os.getenv('CLIENT_ID')
        self.scopes = os.getenv('SCOPES').split(',')

        client_credential = self.get_client_credential()
        self.app = ConfidentialClientApplication(
            client_id=self.client_id,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}",
            client_credential=client_credential
        )

    def get_client_credential(self):
        credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=self.key_vault_url, credential=credential)
        secret = secret_client.get_secret(self.certificate_name)
        
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

    def get_access_token(self):
        result = self.app.acquire_token_for_client(scopes=self.scopes)

        if "access_token" in result:
            return result["access_token"]
        else:
            print("Failed to acquire token:", result.get("error_description", "Unknown error"))
            return None


if __name__ == "__main__":
    print("\nTesting TokenProvider class...")
    token_provider = TokenProvider()
    access_token_1 = token_provider.get_access_token()
    access_token_2 = token_provider.get_access_token()
    print(f"\nAccess Token:\n{token_provider.get_access_token()}")
    print(f"\nAccess Token 2 the same as Access Token 1?: {access_token_1 == access_token_2}")
    print("\nDone.")