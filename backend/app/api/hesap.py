from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import veritabani_al
from app.core.dependencies import aktif_kullanici_getir
from app.core.security import sifre_hashle
from app.models.kullanici import Kullanici
from app.schemas.hesap import HesapCikti, HesapGuncelle

router = APIRouter(
    prefix="/hesap",
    tags=["Hesap"]
)


@router.get("/benim-bilgilerim", response_model=HesapCikti)
def benim_bilgilerim(
    aktif_kullanici: Kullanici = Depends(aktif_kullanici_getir)
):
    return aktif_kullanici


@router.put("/guncelle", response_model=HesapCikti)
def hesap_guncelle(
    veri: HesapGuncelle,
    db: Session = Depends(veritabani_al),
    aktif_kullanici: Kullanici = Depends(aktif_kullanici_getir)
):
    if veri.eposta and veri.eposta != aktif_kullanici.eposta:
        mevcut = db.query(Kullanici).filter(Kullanici.eposta == veri.eposta).first()
        if mevcut:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu e-posta başka bir kullanıcı tarafından kullanılıyor"
            )
        aktif_kullanici.eposta = veri.eposta

    if veri.ad_soyad:
        aktif_kullanici.ad_soyad = veri.ad_soyad

    if veri.sifre:
        aktif_kullanici.sifre_hash = sifre_hashle(veri.sifre)

    db.commit()
    db.refresh(aktif_kullanici)

    return aktif_kullanici