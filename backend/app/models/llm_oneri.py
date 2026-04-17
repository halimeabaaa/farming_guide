from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class LLMOneri(Base):
    __tablename__ = "llm_onerileri"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ciftci_profil_id = Column(Integer, ForeignKey("ciftci_profilleri.id", ondelete="CASCADE"), nullable=False)
    urun_id = Column(Integer, ForeignKey("urunler.id", ondelete="SET NULL"), nullable=True)
    kaynak_model = Column(String(100), nullable=True)
    genel_durum = Column(Text, nullable=False)
    ozet = Column(Text, nullable=False)
    oncelik_puani = Column(Integer, nullable=False)
    ciftciye_not = Column(Text, nullable=False)
    ham_json = Column(Text, nullable=False)
    olusturma_tarihi = Column(DateTime(timezone=True), server_default=func.now())