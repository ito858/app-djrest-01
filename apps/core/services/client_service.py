from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from apps.core.models.cliente import Cliente
from apps.core.models.vip import create_vip_table
from sqlalchemy import MetaData
from my_django_project_001.config.database import engine
import uuid

def generate_dbnome(client_id: int) -> str:
    return f"vip{client_id}"

def generate_token_registrazione() -> str:
    return str(uuid.uuid4())[:32]

def create_client_table(dbnome: str):
    """Create a table with the given dbnome using VIP schema."""
    metadata = MetaData()
    vip_table = create_vip_table(dbnome, metadata)
    with Session(engine) as session:
        vip_table.create(bind=engine, checkfirst=True)
        session.commit()

def add_client(data: dict) -> Cliente:
    with Session(engine) as session:
        client = Cliente(**data)
        session.add(client)
        session.commit()
        session.refresh(client)

        client.dbnome = generate_dbnome(client.id_negozio)
        client.token_registrazione = generate_token_registrazione()
        session.commit()

        create_client_table(client.dbnome)
        return client
