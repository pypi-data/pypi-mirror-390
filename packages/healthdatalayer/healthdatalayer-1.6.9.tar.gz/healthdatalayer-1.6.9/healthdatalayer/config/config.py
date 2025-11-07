import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from .vault import AzureVault

load_dotenv()

vault=AzureVault()

app_env=os.getenv("APP_ENV").lower() # type: ignore

DB_USER_T1 = vault.get_secret(f"milaf-db-{app_env}-username")
DB_PASSWORD_T1 = vault.get_secret(f"milaf-db-{app_env}-password")
DB_HOST_T1 = os.getenv("DATABASE_HOST_T1")
DB_PORT_T1 = os.getenv("DATABASE_PORT_T1")
DB_NAME_T1 = os.getenv("DATABASE_NAME_T1")

DB_PASSWORD_ENCODED_T1 = quote_plus(DB_PASSWORD_T1) # type: ignore

DATABASE_URL_T1 = f"postgresql+psycopg2://{DB_USER_T1}:{DB_PASSWORD_ENCODED_T1}@{DB_HOST_T1}:{DB_PORT_T1}/{DB_NAME_T1}"

DATABASES = {
    "tenant1": DATABASE_URL_T1
}