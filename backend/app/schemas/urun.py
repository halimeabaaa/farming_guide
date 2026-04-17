from pydantic import BaseModel, ConfigDict
from datetime import date, datetime


class UrunOlustur(BaseModel):
    urun_adi: str
    urun_cesidi: str | None = None
    ekim_tarihi: date | None = None
    tahmini_hasat_tarihi: date | None = None
    buyume_asamasi: str | None = None


class UrunGuncelle(BaseModel):
    urun_adi: str | None = None
    urun_cesidi: str | None = None
    ekim_tarihi: date | None = None
    tahmini_hasat_tarihi: date | None = None
    buyume_asamasi: str | None = None


class UrunCikti(BaseModel):
    id: int
    ciftci_profil_id: int
    urun_adi: str
    urun_cesidi: str | None = None
    ekim_tarihi: date | None = None
    tahmini_hasat_tarihi: date | None = None
    buyume_asamasi: str | None = None
    olusturma_tarihi: datetime | None = None
    guncelleme_tarihi: datetime | None = None

    model_config = ConfigDict(from_attributes=True)