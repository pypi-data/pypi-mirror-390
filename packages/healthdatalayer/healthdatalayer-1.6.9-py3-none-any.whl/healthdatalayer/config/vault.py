import os
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient

class AzureVault:
    def __init__(self) -> None:
        credential=ClientSecretCredential(
            tenant_id=os.getenv("AZURE_TENANT_ID",""),
            client_id=os.getenv("AZURE_CLIENT_ID",""),
            client_secret=os.getenv("AZURE_CLIENT_SECRET","")
        )
        self.key_vault_uri=os.getenv("AZURE_KEY_VAULT_URI","")
        self.client=SecretClient(vault_url=self.key_vault_uri,credential=credential)
    
    def get_secret(self,secret_name:str):
        secret=self.client.get_secret(name=secret_name)
        if secret:
            return secret.value
        else:
            raise ValueError("Secret not exist")