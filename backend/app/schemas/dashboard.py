from pydantic import BaseModel
from app.schemas.profil import ProfilCikti
from app.schemas.urun import UrunCikti
from app.schemas.toprak import ToprakCikti
from app.schemas.hava import HavaBugunCikti
from app.schemas.oneri import OneriCikti
from app.schemas.ai_oneri import AIOneriAciklamaCikti


class DashboardOzetCikti(BaseModel):
    profil: ProfilCikti
    urunler: list[UrunCikti]
    aktif_urun: UrunCikti | None = None
    toprak: ToprakCikti | None = None
    hava: HavaBugunCikti | None = None
    bugunku_oneriler: list[OneriCikti]
    ai_oneriler: list[AIOneriAciklamaCikti]