from sqlmodel import create_engine, Session
from .config import DATABASES

engines = {
    tenant: create_engine(url, echo=True)
    for tenant, url in DATABASES.items()
}

def get_session(tenant: str) -> Session:
    if tenant not in engines:
        raise ValueError(f"Tenant {tenant} is not configured")
    return Session(engines[tenant])