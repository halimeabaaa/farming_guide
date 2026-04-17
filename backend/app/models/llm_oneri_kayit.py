from datetime import datetime
from pydantic import BaseModel, ConfigDict


class LLMOneriKayitCikti(BaseModel):
    id: int
    ciftci_profil_id: int
    urun_id: int | None = None
    kaynak_model: str | None = None
    genel_durum: str
    ozet: str
    oncelik_puani: int
    ciftciye_not: str
    ham_json: str
    olusturma_tarihi: datetime | None = None

    model_config = ConfigDict(from_attributes=True)