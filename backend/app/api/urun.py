from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import veritabani_al
from app.core.dependencies import aktif_kullanici_getir
from app.models.kullanici import Kullanici
from app.models.ciftci_profili import CiftciProfili
from app.models.urun import Urun
from app.schemas.urun import UrunOlustur, UrunGuncelle, UrunCikti

router = APIRouter(
    prefix="/urun",
    tags=["Urun"]
)


def kullanicinin_profilini_getir(db: Session, kullanici_id: int):
    profil = db.query(CiftciProfili).filter(
        CiftciProfili.kullanici_id == kullanici_id
    ).first()

    if not profil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Once ciftci profili olusturmaniz gerekiyor"
        )
    return profil


@router.post("/ekle", response_model=UrunCikti)
def urun_ekle(
    urun_verisi: UrunOlustur,
    db: Session = Depends(veritabani_al),
    aktif_kullanici: Kullanici = Depends(aktif_kullanici_getir)
):
    profil = kullanicinin_profilini_getir(db, aktif_kullanici.id)

    yeni_urun = Urun(
        ciftci_profil_id=profil.id,
        urun_adi=urun_verisi.urun_adi,
        urun_cesidi=urun_verisi.urun_cesidi,
        ekim_tarihi=urun_verisi.ekim_tarihi,
        tahmini_hasat_tarihi=urun_verisi.tahmini_hasat_tarihi,
        buyume_asamasi=urun_verisi.buyume_asamasi
    )

    db.add(yeni_urun)
    db.commit()
    db.refresh(yeni_urun)

    return yeni_urun


@router.get("/listele", response_model=list[UrunCikti])
def urunleri_listele(
    db: Session = Depends(veritabani_al),
    aktif_kullanici: Kullanici = Depends(aktif_kullanici_getir)
):
    profil = kullanicinin_profilini_getir(db, aktif_kullanici.id)

    urunler = db.query(Urun).filter(
        Urun.ciftci_profil_id == profil.id
    ).all()

    return urunler


@router.put("/guncelle/{urun_id}", response_model=UrunCikti)
def urun_guncelle(
    urun_id: int,
    urun_verisi: UrunGuncelle,
    db: Session = Depends(veritabani_al),
    aktif_kullanici: Kullanici = Depends(aktif_kullanici_getir)
):
    profil = kullanicinin_profilini_getir(db, aktif_kullanici.id)

    urun = db.query(Urun).filter(
        Urun.id == urun_id,
        Urun.ciftci_profil_id == profil.id
    ).first()

    if not urun:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Urun bulunamadi"
        )

    guncel_veriler = urun_verisi.model_dump(exclude_unset=True)

    for alan, deger in guncel_veriler.items():
        setattr(urun, alan, deger)

    db.commit()
    db.refresh(urun)

    return urun


@router.delete("/sil/{urun_id}")
def urun_sil(
    urun_id: int,
    db: Session = Depends(veritabani_al),
    aktif_kullanici: Kullanici = Depends(aktif_kullanici_getir)
):
    profil = kullanicinin_profilini_getir(db, aktif_kullanici.id)

    urun = db.query(Urun).filter(
        Urun.id == urun_id,
        Urun.ciftci_profil_id == profil.id
    ).first()

    if not urun:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Urun bulunamadi"
        )

    db.delete(urun)
    db.commit()

    return {"mesaj": "Urun silindi"}