from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class IlkSoruCevabi(Base):
    __tablename__ = "ilk_soru_cevaplari"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    kullanici_id = Column(Integer, ForeignKey("kullanicilar.id", ondelete="CASCADE"), nullable=False)
    soru_anahtari = Column(String(100), nullable=False)
    cevap_degeri = Column(Text, nullable=True)
    olusturma_tarihi = Column(DateTime(timezone=True), server_default=func.now())

    kullanici = relationship("Kullanici", back_populates="ilk_soru_cevaplari")