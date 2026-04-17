from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import veritabani_al
from app.core.dependencies import aktif_kullanici_getir
from app.models.kullanici import Kullanici
from app.models.ciftci_profili import CiftciProfili
from app.models.urun import Urun
from app.models.toprak_bilgisi import ToprakBilgisi
from app.schemas.danisman import DanismanSoruIstek, DanismanCevapCikti
from app.services.hava_servisi import bugun_hava_getir, HavaServisiHatasi
from app.services.kural_motoru import bugun_onerilerini_uret
from app.services.openai_danisman_servisi import (
    openai_danisman_cevabi_uret,
    OpenAIDanismanHatasi,
)

router = APIRouter(
    prefix="/danisman",
    tags=["Danisman"]
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


@router.post("/sor", response_model=DanismanCevapCikti)
def danismana_sor(
    istek: DanismanSoruIstek,
    db: Session = Depends(veritabani_al),
    aktif_kullanici: Kullanici = Depends(aktif_kullanici_getir)
):
    profil = profil_getir(db, aktif_kullanici.id)

    urun = db.query(Urun).filter(
        Urun.ciftci_profil_id == profil.id
    ).order_by(Urun.id.desc()).first()

    toprak = db.query(ToprakBilgisi).filter(
        ToprakBilgisi.ciftci_profil_id == profil.id
    ).first()

    hava = None
    try:
        hava = bugun_hava_getir(sehir=profil.sehir, ilce=profil.ilce)
    except HavaServisiHatasi:
        hava = None

    kural_onerileri = []
    if urun and toprak and hava:
        kural_onerileri = bugun_onerilerini_uret(
            urun=urun,
            toprak=toprak,
            hava=hava
        )

    try:
        cevap = openai_danisman_cevabi_uret(
            profil={
                "sehir": profil.sehir,
                "ilce": profil.ilce,
                "arazi_buyuklugu": float(profil.arazi_buyuklugu) if profil.arazi_buyuklugu is not None else None,
                "arazi_birimi": profil.arazi_birimi,
                "sulama_turu": profil.sulama_turu,
                "deneyim_seviyesi": profil.deneyim_seviyesi,
            },
            urun={
                "urun_adi": urun.urun_adi,
                "urun_cesidi": urun.urun_cesidi,
                "ekim_tarihi": str(urun.ekim_tarihi) if urun and urun.ekim_tarihi else None,
                "tahmini_hasat_tarihi": str(urun.tahmini_hasat_tarihi) if urun and urun.tahmini_hasat_tarihi else None,
                "buyume_asamasi": urun.buyume_asamasi if urun else None,
            } if urun else None,
            toprak={
                "toprak_turu": toprak.toprak_turu,
                "ph_degeri": float(toprak.ph_degeri) if toprak and toprak.ph_degeri is not None else None,
                "organik_madde": float(toprak.organik_madde) if toprak and toprak.organik_madde is not None else None,
                "drenaj_durumu": toprak.drenaj_durumu if toprak else None,
                "notlar": toprak.notlar if toprak else None,
            } if toprak else None,
            hava=hava,
            kural_onerileri=kural_onerileri,
            kullanici_sorusu=istek.soru,
            resim_base64=istek.resim_base64,
            resim_mime_turu=istek.resim_mime_turu
        )

        return {
            "soru": istek.soru,
            "cevap": cevap
        }

    except OpenAIDanismanHatasi as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )