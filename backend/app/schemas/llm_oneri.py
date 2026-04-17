from pydantic import BaseModel, ConfigDict


class LLMOneriMadde(BaseModel):
    baslik: str
    aciklama: str
    oneri_turu: str
    risk_seviyesi: str
    uygulanacak_aksiyon: str


class LLMOneriCikti(BaseModel):
    genel_durum: str
    ozet: str
    oncelik_puani: int
    maddeler: list[LLMOneriMadde]
    ciftciye_not: str

    model_config = ConfigDict(from_attributes=True)