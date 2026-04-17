from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import veritabani_al
from app.core.dependencies import aktif_kullanici_getir
from app.models.kullanici import Kullanici
from app.models.ciftci_profili import CiftciProfili
from app.schemas.profil import ProfilOlustur, ProfilGuncelle, ProfilCikti

router = APIRouter(
    prefix="/profil",
    tags=["Profil"]
)


@router.post("/olustur", response_model=ProfilCikti)
def profil_olustur(
    profil_verisi: ProfilOlustur,
    db: Session = Depends(veritabani_al),
    aktif_kullanici: Kullanici = Depends(aktif_kullanici_getir)
):
    mevcut_profil = db.query(CiftciProfili).filter(
        CiftciProfili.kullanici_id == aktif_kullanici.id
    ).first()

    if mevcut_profil:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kullanici icin profil zaten olusturulmus"
        )

    yeni_profil = CiftciProfili(
        kullanici_id=aktif_kullanici.id,
        sehir=profil_verisi.sehir,
        ilce=profil_verisi.ilce,
        arazi_buyuklugu=profil_verisi.arazi_buyuklugu,
        arazi_birimi=profil_verisi.arazi_birimi,
        sulama_turu=profil_verisi.sulama_turu,
        deneyim_seviyesi=profil_verisi.deneyim_seviyesi
    )

    db.add(yeni_profil)
    db.commit()
    db.refresh(yeni_profil)

    return yeni_profil


@router.get("/benim-profilim", response_model=ProfilCikti)
def benim_profilim(
    db: Session = Depends(veritabani_al),
    aktif_kullanici: Kullanici = Depends(aktif_kullanici_getir)
):
    profil = db.query(CiftciProfili).filter(
        CiftciProfili.kullanici_id == aktif_kullanici.id
    ).first()

    if not profil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil bulunamadi"
        )

    return profil


@router.put("/guncelle", response_model=ProfilCikti)
def profil_guncelle(
    profil_verisi: ProfilGuncelle,
    db: Session = Depends(veritabani_al),
    aktif_kullanici: Kullanici = Depends(aktif_kullanici_getir)
):
    profil = db.query(CiftciProfili).filter(
        CiftciProfili.kullanici_id == aktif_kullanici.id
    ).first()

    if not profil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guncellenecek profil bulunamadi"
        )

    guncel_veriler = profil_verisi.model_dump(exclude_unset=True)

    for alan, deger in guncel_veriler.items():
        setattr(profil, alan, deger)

    db.commit()
    db.refresh(profil)

    return profil