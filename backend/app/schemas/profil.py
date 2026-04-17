from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ProfilOlustur(BaseModel):
    sehir: str
    ilce: str | None = None
    arazi_buyuklugu: float | None = None
    arazi_birimi: str | None = None
    sulama_turu: str | None = None
    deneyim_seviyesi: str | None = None


class ProfilGuncelle(BaseModel):
    sehir: str | None = None
    ilce: str | None = None
    arazi_buyuklugu: float | None = None
    arazi_birimi: str | None = None
    sulama_turu: str | None = None
    deneyim_seviyesi: str | None = None


class ProfilCikti(BaseModel):
    id: int
    kullanici_id: int
    sehir: str
    ilce: str | None = None
    arazi_buyuklugu: float | None = None
    arazi_birimi: str | None = None
    sulama_turu: str | None = None
    deneyim_seviyesi: str | None = None
    olusturma_tarihi: datetime | None = None
    guncelleme_tarihi: datetime | None = None

    model_config = ConfigDict(from_attributes=True)