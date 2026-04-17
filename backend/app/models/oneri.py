from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Oneri(Base):
    __tablename__ = "oneriler"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ciftci_profil_id = Column(Integer, ForeignKey("ciftci_profilleri.id", ondelete="CASCADE"), nullable=False)
    urun_id = Column(Integer, ForeignKey("urunler.id", ondelete="SET NULL"), nullable=True)
    oneri_turu = Column(String(50), nullable=False)
    baslik = Column(String(200), nullable=False)
    icerik = Column(Text, nullable=False)
    risk_seviyesi = Column(String(50), nullable=True)
    olusturma_tarihi = Column(DateTime(timezone=True), server_default=func.now())

    ciftci_profili = relationship("CiftciProfili", back_populates="oneriler")
    urun = relationship("Urun", back_populates="oneriler")