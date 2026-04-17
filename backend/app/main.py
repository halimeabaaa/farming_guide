from fastapi import FastAPI
from app.core.database import Base, engine
from app.api.profil import router as profil_router
from app.api.urun import router as urun_router
from app.api.toprak import router as toprak_router
from app.api.hava import router as hava_router
from app.api.oneri import router as oneri_router
from app.api.dashboard import router as dashboard_router
from app.api.ai_oneri import router as ai_oneri_router
from app.api.openai_oneri import router as openai_oneri_router
from app.api.danisman import router as danisman_router
from app.api.hesap import router as hesap_router
# Modelleri yuklemek icin import ediyoruz
from app.models import (
    Kullanici,
    CiftciProfili,
    Urun,
    ToprakBilgisi,
    Oneri,
    IlkSoruCevabi,
    HavaKaydi,
    LLMOneri
)

from app.api.auth import router as auth_router

app = FastAPI(
    title="Ekin Rehberi API",
    description="Ciftcilere yonelik akilli tarim onerileri sunan sistem",
    version="1.0.0"
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # gelistirme icin
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(profil_router)
app.include_router(urun_router)
app.include_router(toprak_router)
app.include_router(hava_router)
app.include_router(oneri_router)
app.include_router(ai_oneri_router)
app.include_router(dashboard_router)
app.include_router(openai_oneri_router)
app.include_router(danisman_router)
app.include_router(hesap_router)

@app.get("/")
def kok():
    return {"mesaj": "Ekin Rehberi API calisiyor"}

@app.get("/saglik")
def saglik_kontrol():
    return {"durum": "iyi"}

