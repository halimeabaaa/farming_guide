from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import veritabani_al
from app.core.dependencies import aktif_kullanici_getir
from app.models.kullanici import Kullanici
from app.models.ciftci_profili import CiftciProfili
from app.models.toprak_bilgisi import ToprakBilgisi
from app.schemas.toprak import ToprakOlustur, ToprakGuncelle, ToprakCikti

router = APIRouter(
    prefix="/toprak",
    tags=["Toprak"]
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


@router.post("/ekle", response_model=ToprakCikti)
def toprak_ekle(
    toprak_verisi: ToprakOlustur,
    db: Session = Depends(veritabani_al),
    aktif_kullanici: Kullanici = Depends(aktif_kullanici_getir)
):
    profil = kullanicinin_profilini_getir(db, aktif_kullanici.id)

    mevcut_toprak = db.query(ToprakBilgisi).filter(
        ToprakBilgisi.ciftci_profil_id == profil.id
    ).first()

    if mevcut_toprak:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu profil icin toprak bilgisi zaten eklenmis"
        )

    yeni_toprak = ToprakBilgisi(
        ciftci_profil_id=profil.id,
        toprak_turu=toprak_verisi.toprak_turu,
        ph_degeri=toprak_verisi.ph_degeri,
        organik_madde=toprak_verisi.organik_madde,
        drenaj_durumu=toprak_verisi.drenaj_durumu,
        notlar=toprak_verisi.notlar
    )

    db.add(yeni_toprak)
    db.commit()
    db.refresh(yeni_toprak)

    return yeni_toprak


@router.get("/getir", response_model=ToprakCikti)
def toprak_getir(
    db: Session = Depends(veritabani_al),
    aktif_kullanici: Kullanici = Depends(aktif_kullanici_getir)
):
    profil = kullanicinin_profilini_getir(db, aktif_kullanici.id)

    toprak = db.query(ToprakBilgisi).filter(
        ToprakBilgisi.ciftci_profil_id == profil.id
    ).first()

    if not toprak:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Toprak bilgisi bulunamadi"
        )

    return toprak


@router.put("/guncelle", response_model=ToprakCikti)
def toprak_guncelle(
    toprak_verisi: ToprakGuncelle,
    db: Session = Depends(veritabani_al),
    aktif_kullanici: Kullanici = Depends(aktif_kullanici_getir)
):
    profil = kullanicinin_profilini_getir(db, aktif_kullanici.id)

    toprak = db.query(ToprakBilgisi).filter(
        ToprakBilgisi.ciftci_profil_id == profil.id
    ).first()

    if not toprak:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guncellenecek toprak bilgisi bulunamadi"
        )

    guncel_veriler = toprak_verisi.model_dump(exclude_unset=True)

    for alan, deger in guncel_veriler.items():
        setattr(toprak, alan, deger)

    db.commit()
    db.refresh(toprak)

    return toprak