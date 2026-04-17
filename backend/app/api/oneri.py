from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import veritabani_al
from app.core.dependencies import aktif_kullanici_getir
from app.models.kullanici import Kullanici
from app.models.ciftci_profili import CiftciProfili
from app.models.urun import Urun
from app.models.toprak_bilgisi import ToprakBilgisi
from app.models.oneri import Oneri
from app.schemas.oneri import BugunOneriSonucu, OneriCikti
from app.services.hava_servisi import bugun_hava_getir, HavaServisiHatasi
from app.services.kural_motoru import bugun_onerilerini_uret

router = APIRouter(
    prefix="/oneri",
    tags=["Oneri"]
)


def profil_getir(db: Session, kullanici_id: int):
    profil = db.query(CiftciProfili).filter(
        CiftciProfili.kullanici_id == kullanici_id
    ).first()

    if not profil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Once ciftci profili olusturmaniz gerekiyor"
        )
    return profil


@router.post("/bugun-uret", response_model=BugunOneriSonucu)
def bugun_oneri_uret(
    db: Session = Depends(veritabani_al),
    aktif_kullanici: Kullanici = Depends(aktif_kullanici_getir)
):
    profil = profil_getir(db, aktif_kullanici.id)

    urun = db.query(Urun).filter(
        Urun.ciftci_profil_id == profil.id
    ).order_by(Urun.id.desc()).first()

    if not urun:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Once en az bir urun eklemeniz gerekiyor"
        )

    toprak = db.query(ToprakBilgisi).filter(
        ToprakBilgisi.ciftci_profil_id == profil.id
    ).first()

    if not toprak:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Once toprak bilgisi eklemeniz gerekiyor"
        )

    try:
        hava = bugun_hava_getir(sehir=profil.sehir, ilce=profil.ilce)
    except HavaServisiHatasi as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Ayni gun tekrar uretildiyse once eski bugun onerilerini sil
    eski_oneriler = db.query(Oneri).filter(
        Oneri.ciftci_profil_id == profil.id,
        func.date(Oneri.olusturma_tarihi) == date.today()
    ).all()

    for eski in eski_oneriler:
        db.delete(eski)
    db.commit()

    yeni_oneriler_dict = bugun_onerilerini_uret(urun=urun, toprak=toprak, hava=hava)

    kaydedilenler = []
    for oneri_dict in yeni_oneriler_dict:
        kayit = Oneri(
            ciftci_profil_id=profil.id,
            urun_id=urun.id,
            oneri_turu=oneri_dict["oneri_turu"],
            baslik=oneri_dict["baslik"],
            icerik=oneri_dict["icerik"],
            risk_seviyesi=oneri_dict["risk_seviyesi"]
        )
        db.add(kayit)
        kaydedilenler.append(kayit)

    db.commit()

    bugunku_oneriler = db.query(Oneri).filter(
        Oneri.ciftci_profil_id == profil.id,
        func.date(Oneri.olusturma_tarihi) == date.today()
    ).order_by(Oneri.id.asc()).all()

    return {
        "hava": hava,
        "oneriler": bugunku_oneriler
    }


@router.get("/gecmis", response_model=list[OneriCikti])
def oneri_gecmisi(
    db: Session = Depends(veritabani_al),
    aktif_kullanici: Kullanici = Depends(aktif_kullanici_getir)
):
    profil = profil_getir(db, aktif_kullanici.id)

    oneriler = db.query(Oneri).filter(
        Oneri.ciftci_profil_id == profil.id
    ).order_by(Oneri.olusturma_tarihi.desc()).all()

    return oneriler