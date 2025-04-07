from sqlalchemy import Column, Integer, String, Boolean, DateTime, DECIMAL, Text
from sqlalchemy.sql import func
from .base import Base

class Cliente(Base):
    __tablename__ = "cliente"

    id_negozio = Column(Integer, primary_key=True, autoincrement=True)
    nome_negozio = Column(String(255), nullable=False, default="")
    tipo_negozio = Column(String(50), default="")
    indirizzo = Column(String(255), default="")
    citta = Column(String(100), default="")
    provincia = Column(String(50), default="")
    cap = Column(String(10), default="")
    telefono = Column(String(20), default="")
    email = Column(String(255), default="")
    sito_web = Column(String(255), default="")
    partita_iva = Column(String(11), unique=True, nullable=True)
    data_creazione = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    attivo = Column(Boolean, default=True)  # Using Boolean for tinyint(1)
    coordinate_latitudine = Column(DECIMAL(10, 8), nullable=True)
    coordinate_longitudine = Column(DECIMAL(11, 8), nullable=True)
    descrizione = Column(Text, nullable=True)
    orari_apertura = Column(String(255), default="")
    token_registrazione = Column(String(32), unique=True, nullable=True)
    data_scadenza_token = Column(DateTime, nullable=False, default="0000-00-00 00:00:00")
    active = Column(Boolean, default=True)  # Second 'active' field as per SQL
    dbnome = Column(String(255), nullable=False, default="")

    def __repr__(self):
        return f"<Cliente(id_negozio={self.id_negozio}, nome_negozio='{self.nome_negozio}')>"
