from sqlalchemy import Column, BigInteger, String, SmallInteger, Integer, Float, DateTime, BINARY
from sqlalchemy.sql import func
from .base import Base

class VIP(Base):
    __tablename__ = "vip"  # Base name, will be overridden by dbnome

    IDvip = Column(BigInteger, primary_key=True)
    code = Column(String(13), nullable=True, index=True)
    nascita = Column(String(255), nullable=True)
    cellulare = Column(String(255), nullable=True)
    sms = Column(SmallInteger, default=0)
    Punti = Column(Integer, nullable=True)
    Sconto = Column(Integer, nullable=True)
    Ck = Column(String(255), nullable=True)
    idata = Column(DateTime, server_default=func.now())
    ioperatore = Column(Integer, nullable=True)
    inegozio = Column(Integer, nullable=True)
    P_cs = Column(Integer, default=0)
    P_ldata = Column(String(255), nullable=True)
    P_importo = Column(Float, default=0.00)
    Nome = Column(String(255), nullable=True)
    Indirizzo = Column(String(255), nullable=True)
    Cap = Column(String(255), nullable=True)
    Citta = Column(String(255), nullable=True)
    Prov = Column(String(255), nullable=True)
    CodiceFiscale = Column(String(255), nullable=True)
    PartitaIva = Column(String(255), nullable=True)
    Email = Column(String(255), nullable=True)
    sesso = Column(Integer, default=0)
    VIPanno = Column(Integer, default=0)
    maps = Column(String(255), nullable=True)
    VIPscadenza = Column(String(255), nullable=True)
    Blocco = Column(Integer, default=0)
    cognome = Column(String(255), default='')
    SerBlocco = Column(Integer, default=0)
    SerBloccoBz = Column(String(255), nullable=True)
    omail = Column(SmallInteger, default=0)
    oposte = Column(SmallInteger, default=0)
    msg = Column(Integer, default=0)
    msgstr = Column(String(255), nullable=True)
    utime = Column(String(255), nullable=True)
    upc = Column(String(255), nullable=True)
    uzt = Column(Integer, default=0)
    un = Column(String(255), nullable=True)
    lotteria = Column(String(20), nullable=True)
    statoanno = Column(String(10), nullable=True)
    img = Column(BINARY, nullable=True)
    n = Column(String(255), nullable=True)
    SCOscadenza = Column(String(20), nullable=True)
    stato = Column(SmallInteger, default=0)  # 0 means taken, 1 means available

    def __repr__(self):
        return f"VIP({self.Nome} {self.cognome} - {self.code})"
