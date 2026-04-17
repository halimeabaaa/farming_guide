from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.schemas.hava import HavaBugunCikti


class OneriCikti(BaseModel):
    id: int
    ciftci_profil_id: int
    urun_id: int | None = None
    oneri_turu: str
    baslik: str
    icerik: str
    risk_seviyesi: str | None = None
    olusturma_tarihi: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class BugunOneriSonucu(BaseModel):
    hava: HavaBugunCikti
    oneriler: list[OneriCikti]