from sqlalchemy import Column, BigInteger, String, SmallInteger, Integer, Float, DateTime, BINARY, Table, MetaData
from sqlalchemy.sql import func
from .base import Base

class VIP(Base):
    __tablename__ = "vip"  # Base name, will be overridden dynamically

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
    stato = Column(SmallInteger, default=0)

    def __repr__(self):
        return f"VIP({self.Nome} {self.cognome} - {self.code})"

def create_vip_table(dbnome: str, metadata: MetaData) -> Table:
    """Create a VIP table schema dynamically for the given dbnome."""
    return Table(
        dbnome, metadata,
        Column('IDvip', BigInteger, primary_key=True),
        Column('code', String(13), nullable=True, index=True),
        Column('nascita', String(255), nullable=True),
        Column('cellulare', String(255), nullable=True),
        Column('sms', SmallInteger, default=0),
        Column('Punti', Integer, nullable=True),
        Column('Sconto', Integer, nullable=True),
        Column('Ck', String(255), nullable=True),
        Column('idata', DateTime, server_default=func.now()),
        Column('ioperatore', Integer, nullable=True),
        Column('inegozio', Integer, nullable=True),
        Column('P_cs', Integer, default=0),
        Column('P_ldata', String(255), nullable=True),
        Column('P_importo', Float, default=0.00),
        Column('Nome', String(255), nullable=True),
        Column('Indirizzo', String(255), nullable=True),
        Column('Cap', String(255), nullable=True),
        Column('Citta', String(255), nullable=True),
        Column('Prov', String(255), nullable=True),
        Column('CodiceFiscale', String(255), nullable=True),
        Column('PartitaIva', String(255), nullable=True),
        Column('Email', String(255), nullable=True),
        Column('sesso', Integer, default=0),
        Column('VIPanno', Integer, default=0),
        Column('maps', String(255), nullable=True),
        Column('VIPscadenza', String(255), nullable=True),
        Column('Blocco', Integer, default=0),
        Column('cognome', String(255), default=''),
        Column('SerBlocco', Integer, default=0),
        Column('SerBloccoBz', String(255), nullable=True),
        Column('omail', SmallInteger, default=0),
        Column('oposte', SmallInteger, default=0),
        Column('msg', Integer, default=0),
        Column('msgstr', String(255), nullable=True),
        Column('utime', String(255), nullable=True),
        Column('upc', String(255), nullable=True),
        Column('uzt', Integer, default=0),
        Column('un', String(255), nullable=True),
        Column('lotteria', String(20), nullable=True),
        Column('statoanno', String(10), nullable=True),
        Column('img', BINARY, nullable=True),
        Column('n', String(255), nullable=True),
        Column('SCOscadenza', String(20), nullable=True),
        Column('stato', SmallInteger, default=0),
        extend_existing=True
    )
