from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import ayarlar
from app.core.database import veritabani_al
from app.core.security import sifre_hashle, sifre_dogrula, access_token_olustur
from app.models.kullanici import Kullanici
from app.schemas.kullanici import KullaniciKayit, KullaniciCikti
from app.schemas.token import Token

router = APIRouter(
    prefix="/kimlik",
    tags=["Kimlik"]
)


@router.post("/kayit-ol", response_model=KullaniciCikti)
def kayit_ol(kullanici_verisi: KullaniciKayit, db: Session = Depends(veritabani_al)):
    mevcut_kullanici = db.query(Kullanici).filter(Kullanici.eposta == kullanici_verisi.eposta).first()
    if mevcut_kullanici:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu e-posta ile kayitli bir kullanici zaten var"
        )

    yeni_kullanici = Kullanici(
        ad_soyad=kullanici_verisi.ad_soyad,
        eposta=kullanici_verisi.eposta,
        sifre_hash=sifre_hashle(kullanici_verisi.sifre)
    )

    db.add(yeni_kullanici)
    db.commit()
    db.refresh(yeni_kullanici)

    return yeni_kullanici


@router.post("/giris-yap", response_model=Token)
def giris_yap(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(veritabani_al)
):
    kullanici = db.query(Kullanici).filter(Kullanici.eposta == form_data.username).first()

    if not kullanici or not sifre_dogrula(form_data.password, kullanici.sifre_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-posta veya sifre hatali"
        )

    access_token_expires = timedelta(minutes=ayarlar.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = access_token_olustur(
        data={"sub": kullanici.eposta},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }