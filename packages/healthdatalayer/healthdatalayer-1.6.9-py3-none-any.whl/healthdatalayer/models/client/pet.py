import uuid
from healthdatalayer.models import Client
from typing import Optional
from sqlmodel import Field, Relationship

from .client_type import ClientType
from .px import Px

class Pet(Client, table=True):
    __tablename__ = "pet"

    parent_id:Optional[uuid.UUID]=Field(default=None,foreign_key="px.client_id")
    parent: Optional[Px] = Relationship()

    client_type_id:Optional[uuid.UUID]=Field(default=None,foreign_key="client_type.client_type_id")
    client_type: Optional[ClientType] = Relationship()