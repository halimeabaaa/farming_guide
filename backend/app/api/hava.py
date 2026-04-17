from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import veritabani_al
from app.core.dependencies import aktif_kullanici_getir
from app.models.kullanici import Kullanici
from app.models.ciftci_profili import CiftciProfili
from app.schemas.hava import HavaBugunCikti
from app.services.hava_servisi import bugun_hava_getir, HavaServisiHatasi

router = APIRouter(
    prefix="/hava",
    tags=["Hava"]
)


@router.get("/bugun", response_model=HavaBugunCikti)
def hava_bugun(
    db: Session = Depends(veritabani_al),
    aktif_kullanici: Kullanici = Depends(aktif_kullanici_getir)
):
    profil = db.query(CiftciProfili).filter(
        CiftciProfili.kullanici_id == aktif_kullanici.id
    ).first()

    if not profil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Once ciftci profili olusturmaniz gerekiyor"
        )

    try:
        hava = bugun_hava_getir(sehir=profil.sehir, ilce=profil.ilce)
        return hava

    except HavaServisiHatasi as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Beklenmeyen hata: {str(e)}"
        )