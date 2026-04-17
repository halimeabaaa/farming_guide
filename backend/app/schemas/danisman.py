from pydantic import BaseModel


class DanismanSoruIstek(BaseModel):
    soru: str
    resim_base64: str | None = None
    resim_mime_turu: str | None = None
    resim_dosya_adi: str | None = None


class DanismanCevapCikti(BaseModel):
    soru: str
    cevap: str