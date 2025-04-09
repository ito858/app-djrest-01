from sqlalchemy.orm import Session
from sqlalchemy import MetaData
from apps.core.models.vip import create_vip_table
from my_django_project_001.config.database import engine
import pandas as pd

def upload_vip_data(df: pd.DataFrame, dbnome: str):
    """Upload VIP data to the specified dbnome table."""
    metadata = MetaData()
    vip_table = create_vip_table(dbnome, metadata)

    with Session(engine) as session:
        vip_table.create(bind=engine, checkfirst=True)

        records = df.to_dict(orient='records')
        for record in records:
            insert_data = {k: v for k, v in record.items() if k in vip_table.columns}
            session.execute(vip_table.insert().values(**insert_data))
        session.commit()
