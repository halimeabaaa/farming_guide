from sqlalchemy import Column, Integer, String, Date, DateTime, DECIMAL
from sqlalchemy.sql import func
from app.core.database import Base


class HavaKaydi(Base):
    __tablename__ = "hava_kayitlari"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sehir = Column(String(100), nullable=False)
    ilce = Column(String(100), nullable=True)
    kayit_tarihi = Column(Date, nullable=False)
    sicaklik = Column(DECIMAL(5, 2), nullable=True)
    nem = Column(DECIMAL(5, 2), nullable=True)
    yagis_miktari = Column(DECIMAL(6, 2), nullable=True)
    ruzgar_hizi = Column(DECIMAL(6, 2), nullable=True)
    hava_aciklamasi = Column(String(150), nullable=True)
    olusturma_tarihi = Column(DateTime(timezone=True), server_default=func.now())