from pydantic import BaseModel


class AIOneriAciklamaIstek(BaseModel):
    urun_adi: str
    toprak_turu: str
    sehir: str
    ilce: str | None = None
    sicaklik_max: float | None = None
    sicaklik_min: float | None = None
    yagis_toplami: float | None = None
    yagis_ihtimali_max: float | None = None
    ruzgar_hizi_max: float | None = None
    ortalama_nem: float | None = None
    eto: float | None = None
    baslik: str
    icerik: str
    risk_seviyesi: str | None = None
    oneri_turu: str


class AIOneriAciklamaCikti(BaseModel):
    baslik: str
    aciklama: str
    risk_seviyesi: str | None = None
    oneri_turu: str