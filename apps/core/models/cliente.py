from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func  # Add this import
from .base import Base

class Cliente(Base):
    __tablename__ = "cliente"

    id_negozio = Column(Integer, primary_key=True, autoincrement=True)
    nome_negozio = Column(String(255), nullable=False, default='')
    tipo_negozio = Column(String(50), default='')
    indirizzo = Column(String(255), default='')
    citta = Column(String(100), default='')
    provincia = Column(String(50), default='')
    cap = Column(String(10), default='')
    telefono = Column(String(20), default='')
    email = Column(String(255), default='')
    partita_iva = Column(String(11), nullable=True)
    data_creazione = Column(DateTime, server_default=func.now())
    token_registrazione = Column(String(16), nullable=True, unique=True)
    data_scadenza_token = Column(DateTime, default='0000-00-00 00:00:00')
    dbnome = Column(String(255), nullable=False, default='')

    def __repr__(self):
        return f"Cliente(id={self.id_negozio}, nome={self.nome_negozio})"
