from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class HesapCikti(BaseModel):
    id: int
    ad_soyad: str
    eposta: EmailStr
    olusturma_tarihi: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class HesapGuncelle(BaseModel):
    ad_soyad: str | None = None
    eposta: EmailStr | None = None
    sifre: str | None = None