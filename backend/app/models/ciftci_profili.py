from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class CiftciProfili(Base):
    __tablename__ = "ciftci_profilleri"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    kullanici_id = Column(Integer, ForeignKey("kullanicilar.id", ondelete="CASCADE"), nullable=False)
    sehir = Column(String(100), nullable=False)
    ilce = Column(String(100), nullable=True)
    arazi_buyuklugu = Column(DECIMAL(10, 2), nullable=True)
    arazi_birimi = Column(String(50), nullable=True)
    sulama_turu = Column(String(50), nullable=True)
    deneyim_seviyesi = Column(String(50), nullable=True)
    olusturma_tarihi = Column(DateTime(timezone=True), server_default=func.now())
    guncelleme_tarihi = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    kullanici = relationship("Kullanici", back_populates="ciftci_profilleri")
    urunler = relationship("Urun", back_populates="ciftci_profili", cascade="all, delete-orphan")
    toprak_bilgileri = relationship("ToprakBilgisi", back_populates="ciftci_profili", cascade="all, delete-orphan")
    oneriler = relationship("Oneri", back_populates="ciftci_profili", cascade="all, delete-orphan")