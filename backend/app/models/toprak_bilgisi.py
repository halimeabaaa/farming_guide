from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class ToprakBilgisi(Base):
    __tablename__ = "toprak_bilgileri"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ciftci_profil_id = Column(Integer, ForeignKey("ciftci_profilleri.id", ondelete="CASCADE"), nullable=False)
    toprak_turu = Column(String(100), nullable=False)
    ph_degeri = Column(DECIMAL(4, 2), nullable=True)
    organik_madde = Column(DECIMAL(5, 2), nullable=True)
    drenaj_durumu = Column(String(50), nullable=True)
    notlar = Column(Text, nullable=True)
    olusturma_tarihi = Column(DateTime(timezone=True), server_default=func.now())
    guncelleme_tarihi = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    ciftci_profili = relationship("CiftciProfili", back_populates="toprak_bilgileri")