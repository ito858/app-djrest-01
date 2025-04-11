from sqlalchemy.orm import Session
from apps.core.models.cliente import Cliente
from apps.core.models.vip import create_vip_table
from my_django_project_001.config.database import engine
from sqlalchemy import MetaData
import uuid

# Define valid Cliente fields for modularity
CLIENTE_FIELDS = {
    'mandatory': {
        'nome_negozio': str,
        'telefono': str,
    },
    'optional': {
        'tipo_negozio': str,
        'indirizzo': str,
        'citta': str,
        'provincia': str,
        'cap': str,
        'email': str,
        'partita_iva': str,
    }
}

def generate_dbnome(client_id: int) -> str:
    return f"vip{client_id}"

def generate_token_registrazione(session: Session) -> str:
    while True:
        token = str(uuid.uuid4())[:16]
        if not session.query(Cliente).filter(Cliente.token_registrazione == token).first():
            return token

def create_client_table(dbnome: str):
    metadata = MetaData()
    vip_table = create_vip_table(dbnome, metadata)
    with Session(engine) as session:
        vip_table.create(bind=engine, checkfirst=True)
        session.commit()

def create_cliente_table():
    """Ensure the cliente table exists."""
    metadata = MetaData()
    Cliente.__table__.create(bind=engine, checkfirst=True)

def add_client(data: dict) -> Cliente:
    with Session(engine) as session:
        # Ensure cliente table exists
        create_cliente_table()

        # Filter data to only include valid Cliente fields
        valid_data = {k: v for k, v in data.items() if k in CLIENTE_FIELDS['mandatory'] or k in CLIENTE_FIELDS['optional']}
        client = Cliente(**valid_data)
        session.add(client)
        session.commit()
        session.refresh(client)

        client.dbnome = generate_dbnome(client.id_negozio)
        client.token_registrazione = generate_token_registrazione(session)
        session.commit()

        create_client_table(client.dbnome)
        return client

def update_client(client_id: int, data: dict) -> Cliente:
    with Session(engine) as session:
        client = session.query(Cliente).filter(Cliente.id_negozio == client_id).first()
        if not client:
            return None

        valid_data = {k: v for k, v in data.items() if k in CLIENTE_FIELDS['mandatory'] or k in CLIENTE_FIELDS['optional']}
        for key, value in valid_data.items():
            if key == 'token_registrazione' and value != client.token_registrazione:
                client.token_registrazione = value
            elif hasattr(client, key):
                setattr(client, key, value)

        session.commit()
        return client

def regenerate_token(client_id: int) -> Cliente:
    with Session(engine) as session:
        client = session.query(Cliente).filter(Cliente.id_negozio == client_id).first()
        if not client:
            return None
        client.token_registrazione = generate_token_registrazione(session)
        session.commit()
        return client
