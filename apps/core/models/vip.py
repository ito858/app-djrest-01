from sqlalchemy import Column, Integer, String, DateTime, SmallInteger, Table
from sqlalchemy.sql import func
from .base import Base

class VIP(Base):
    __tablename__ = "vip"

    IDvip = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(13), nullable=False, default='', unique=True, index=True)
    Nome = Column(String(50))
    cognome = Column(String(50), default='')
    cellulare = Column(String(30), default='', index=True)
    nascita = Column(String(30), default='')
    Indirizzo = Column(String(255), default='')
    Cap = Column(String(40), default='')
    Citta = Column(String(50), default='')
    Prov = Column(String(20), default='')
    Email = Column(String(100), default='')
    sesso = Column(Integer, default=0)
    idata = Column(DateTime, server_default=func.now())
    rdata = Column(DateTime, default='')
    stato = Column(SmallInteger, default=0, index=True)

    def __repr__(self):
        return f"VIP({self.Nome} {self.cognome} - {self.code})"

def create_vip_table(dbnome: str, metadata) -> Table:
    return Table(
        dbnome, metadata,
        Column('IDvip', Integer, primary_key=True, autoincrement=True),
        Column('code', String(13), nullable=False, default='', unique=True, index=True),
        Column('Nome', String(50)),
        Column('cognome', String(50), default=''),
        Column('cellulare', String(30), default='', index=True),
        Column('nascita', String(30), default=''),
        Column('Indirizzo', String(255), default=''),
        Column('Cap', String(40), default=''),
        Column('Citta', String(50), default=''),
        Column('Prov', String(20), default=''),
        Column('Email', String(100), default=''),
        Column('sesso', Integer, default=0),
        Column('idata', DateTime, server_default=func.now()),
        Column('rdata', DateTime, default=''),
        Column('stato', SmallInteger, default=0, index=True),
        extend_existing=True
    )
