from pydantic import BaseModel


class HavaBugunCikti(BaseModel):
    sehir: str
    ilce: str | None = None
    enlem: float
    boylam: float
    zaman_dilimi: str
    tarih: str
    sicaklik_max: float | None = None
    sicaklik_min: float | None = None
    yagis_toplami: float | None = None
    yagis_ihtimali_max: float | None = None
    ruzgar_hizi_max: float | None = None
    ortalama_nem: float | None = None
    eto: float | None = None