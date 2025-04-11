from sqlalchemy.orm import Session
from sqlalchemy import MetaData
from apps.core.models.vip import create_vip_table
from my_django_project_001.config.database import engine
import pandas as pd

def upload_vip_data(df: pd.DataFrame, dbnome: str):
    """Upload VIP data with only code column, other fields empty, stato=1."""
    metadata = MetaData()
    vip_table = create_vip_table(dbnome, metadata)

    with Session(engine) as session:
        # Ensure table exists
        vip_table.create(bind=engine, checkfirst=True)

        # Prepare records with defaults
        records = [
            {
                'code': str(row['code']),  # Ensure string type
                'Nome': '',
                'cognome': '',
                'cellulare': '',
                'nascita': '',
                'Indirizzo': '',
                'Cap': '',
                'Citta': '',
                'Prov': '',
                'Email': '',
                'sesso': 0,
                'rdata': '',
                'stato': 1  # Preassigned, not taken
            } for _, row in df.iterrows()
        ]

        # Insert records
        session.execute(vip_table.insert(), records)
        session.commit()
