from sqlalchemy.orm import Session
from apps.core.models.cliente import Cliente
from sqlalchemy.sql import text
from my_django_project_001.config.database import engine  # Absolute import
import uuid  # For token generation placeholder

def generate_dbnome(client_id: int) -> str:
    """Generate dbnome based on client ID (modular for future changes)."""
    return f"vip{client_id}"

def generate_token_registrazione() -> str:
    """Generate token_registrazione (modular placeholder)."""
    return str(uuid.uuid4())[:10]  # Temporary UUID, truncated to 32 chars

def create_client_table(dbnome: str):
    """Create a table with the given dbnome (modular placeholder)."""
    with Session(engine) as session:
        # Placeholder: Add actual table creation logic later
        session.execute(text(f"CREATE TABLE IF NOT EXISTS {dbnome} (id INTEGER PRIMARY KEY)"))
        session.commit()

def add_client(data: dict) -> Cliente:
    """Add a client to the cliente table."""
    with Session(engine) as session:
        client = Cliente(**data)
        session.add(client)
        session.commit()
        session.refresh(client)  # Get the ID

        # Set dbnome and token after ID is assigned
        client.dbnome = generate_dbnome(client.id_negozio)
        client.token_registrazione = generate_token_registrazione()
        session.commit()

        # Create the table
        create_client_table(client.dbnome)
        return client
