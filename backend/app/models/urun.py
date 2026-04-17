from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Urun(Base):
    __tablename__ = "urunler"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ciftci_profil_id = Column(Integer, ForeignKey("ciftci_profilleri.id", ondelete="CASCADE"), nullable=False)
    urun_adi = Column(String(100), nullable=False)
    urun_cesidi = Column(String(100), nullable=True)
    ekim_tarihi = Column(Date, nullable=True)
    tahmini_hasat_tarihi = Column(Date, nullable=True)
    buyume_asamasi = Column(String(50), nullable=True)
    olusturma_tarihi = Column(DateTime(timezone=True), server_default=func.now())
    guncelleme_tarihi = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    ciftci_profili = relationship("CiftciProfili", back_populates="urunler")
    oneriler = relationship("Oneri", back_populates="urun")