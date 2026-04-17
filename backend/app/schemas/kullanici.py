from pydantic import BaseModel, EmailStr
from datetime import datetime


class KullaniciKayit(BaseModel):
    ad_soyad: str
    eposta: EmailStr
    sifre: str


class KullaniciGiris(BaseModel):
    eposta: EmailStr
    sifre: str


class KullaniciCikti(BaseModel):
    id: int
    ad_soyad: str
    eposta: EmailStr
    olusturma_tarihi: datetime | None = None

    class Config:
        from_attributes = True