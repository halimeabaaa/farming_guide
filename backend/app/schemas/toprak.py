from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ToprakOlustur(BaseModel):
    toprak_turu: str
    ph_degeri: float | None = None
    organik_madde: float | None = None
    drenaj_durumu: str | None = None
    notlar: str | None = None


class ToprakGuncelle(BaseModel):
    toprak_turu: str | None = None
    ph_degeri: float | None = None
    organik_madde: float | None = None
    drenaj_durumu: str | None = None
    notlar: str | None = None


class ToprakCikti(BaseModel):
    id: int
    ciftci_profil_id: int
    toprak_turu: str
    ph_degeri: float | None = None
    organik_madde: float | None = None
    drenaj_durumu: str | None = None
    notlar: str | None = None
    olusturma_tarihi: datetime | None = None
    guncelleme_tarihi: datetime | None = None

    model_config = ConfigDict(from_attributes=True)