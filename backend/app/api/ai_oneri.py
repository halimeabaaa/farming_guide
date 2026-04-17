from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import veritabani_al
from app.core.dependencies import aktif_kullanici_getir
from app.models.kullanici import Kullanici
from app.models.ciftci_profili import CiftciProfili
from app.models.urun import Urun
from app.models.toprak_bilgisi import ToprakBilgisi
from app.models.oneri import Oneri
from app.schemas.ai_oneri import AIOneriAciklamaIstek, AIOneriAciklamaCikti
from app.services.hava_servisi import bugun_hava_getir, HavaServisiHatasi
from app.services.ai_aciklama_servisi import ai_destekli_oneri_acikla

router = APIRouter(
    prefix="/ai-oneri",
    tags=["AI Oneri"]
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


@router.get("/bugun", response_model=list[AIOneriAciklamaCikti])
def bugunku_ai_onerileri(
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

    bugunku_oneriler = db.query(Oneri).filter(
        Oneri.ciftci_profil_id == profil.id
    ).order_by(Oneri.olusturma_tarihi.desc()).all()

    if not bugunku_oneriler:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kayitli oneri bulunamadi. Once /oneri/bugun-uret calistirin"
        )

    try:
        hava = bugun_hava_getir(sehir=profil.sehir, ilce=profil.ilce)
    except HavaServisiHatasi as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    sonuc = []

    for oneri in bugunku_oneriler:
        istek = AIOneriAciklamaIstek(
            urun_adi=urun.urun_adi,
            toprak_turu=toprak.toprak_turu,
            sehir=profil.sehir,
            ilce=profil.ilce,
            sicaklik_max=hava.get("sicaklik_max"),
            sicaklik_min=hava.get("sicaklik_min"),
            yagis_toplami=hava.get("yagis_toplami"),
            yagis_ihtimali_max=hava.get("yagis_ihtimali_max"),
            ruzgar_hizi_max=hava.get("ruzgar_hizi_max"),
            ortalama_nem=hava.get("ortalama_nem"),
            eto=hava.get("eto"),
            baslik=oneri.baslik,
            icerik=oneri.icerik,
            risk_seviyesi=oneri.risk_seviyesi,
            oneri_turu=oneri.oneri_turu
        )

        sonuc.append(ai_destekli_oneri_acikla(istek))

    return sonuc