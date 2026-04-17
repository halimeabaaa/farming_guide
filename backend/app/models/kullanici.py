from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Kullanici(Base):
    __tablename__ = "kullanicilar"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ad_soyad = Column(String(150), nullable=False)
    eposta = Column(String(150), unique=True, nullable=False, index=True)
    sifre_hash = Column(String(255), nullable=False)
    olusturma_tarihi = Column(DateTime(timezone=True), server_default=func.now())
    guncelleme_tarihi = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    ciftci_profilleri = relationship("CiftciProfili", back_populates="kullanici", cascade="all, delete-orphan")
    ilk_soru_cevaplari = relationship("IlkSoruCevabi", back_populates="kullanici", cascade="all, delete-orphan")