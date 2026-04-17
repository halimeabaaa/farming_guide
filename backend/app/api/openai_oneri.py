import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import ayarlar
from app.core.database import veritabani_al
from app.core.dependencies import aktif_kullanici_getir
from app.models.kullanici import Kullanici
from app.models.ciftci_profili import CiftciProfili
from app.models.urun import Urun
from app.models.toprak_bilgisi import ToprakBilgisi
from app.models.llm_oneri import LLMOneri
from app.services.hava_servisi import bugun_hava_getir, HavaServisiHatasi
from app.services.kural_motoru import bugun_onerilerini_uret
from app.services.openai_oneri_servisi import (
    openai_tarim_onerisi_uret,
    OpenAIOneriHatasi,
)
from app.schemas.llm_oneri import LLMOneriCikti
from app.schemas.llm_oneri_kayit import LLMOneriKayitCikti

router = APIRouter(
    prefix="/openai-oneri",
    tags=["OpenAI Oneri"]
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


def urun_toprak_hava_hazirla(db: Session, profil):
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

    return urun, toprak, hava


def llm_sonucu_uret(profil, urun, toprak, hava):
    kural_onerileri = bugun_onerilerini_uret(
        urun=urun,
        toprak=toprak,
        hava=hava
    )

    return openai_tarim_onerisi_uret(
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
            "ekim_tarihi": str(urun.ekim_tarihi) if urun.ekim_tarihi else None,
            "tahmini_hasat_tarihi": str(urun.tahmini_hasat_tarihi) if urun.tahmini_hasat_tarihi else None,
            "buyume_asamasi": urun.buyume_asamasi,
        },
        toprak={
            "toprak_turu": toprak.toprak_turu,
            "ph_degeri": float(toprak.ph_degeri) if toprak.ph_degeri is not None else None,
            "organik_madde": float(toprak.organik_madde) if toprak.organik_madde is not None else None,
            "drenaj_durumu": toprak.drenaj_durumu,
            "notlar": toprak.notlar,
        },
        hava=hava,
        kural_tabanli_oneriler=kural_onerileri
    )


@router.get("/bugun", response_model=LLMOneriCikti)
def openai_bugunku_oneri(
    db: Session = Depends(veritabani_al),
    aktif_kullanici: Kullanici = Depends(aktif_kullanici_getir)
):
    profil = profil_getir(db, aktif_kullanici.id)
    urun, toprak, hava = urun_toprak_hava_hazirla(db, profil)

    try:
        sonuc = llm_sonucu_uret(profil, urun, toprak, hava)
        return sonuc

    except OpenAIOneriHatasi as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Beklenmeyen openai endpoint hatasi: {type(e).__name__}: {str(e)}"
        )


@router.post("/bugun-kaydet", response_model=LLMOneriKayitCikti)
def openai_bugunku_oneri_kaydet(
    db: Session = Depends(veritabani_al),
    aktif_kullanici: Kullanici = Depends(aktif_kullanici_getir)
):
    profil = profil_getir(db, aktif_kullanici.id)
    urun, toprak, hava = urun_toprak_hava_hazirla(db, profil)

    try:
        sonuc = llm_sonucu_uret(profil, urun, toprak, hava)

        kayit = LLMOneri(
            ciftci_profil_id=profil.id,
            urun_id=urun.id,
            kaynak_model=ayarlar.OPENAI_MODEL,
            genel_durum=sonuc.genel_durum,
            ozet=sonuc.ozet,
            oncelik_puani=sonuc.oncelik_puani,
            ciftciye_not=sonuc.ciftciye_not,
            ham_json=json.dumps(sonuc.model_dump(), ensure_ascii=False)
        )

        db.add(kayit)
        db.commit()
        db.refresh(kayit)

        return kayit

    except OpenAIOneriHatasi as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Kayit sirasinda hata: {type(e).__name__}: {str(e)}"
        )


@router.get("/gecmis", response_model=list[LLMOneriKayitCikti])
def openai_oneri_gecmisi(
    db: Session = Depends(veritabani_al),
    aktif_kullanici: Kullanici = Depends(aktif_kullanici_getir)
):
    profil = profil_getir(db, aktif_kullanici.id)

    kayitlar = db.query(LLMOneri).filter(
        LLMOneri.ciftci_profil_id == profil.id
    ).order_by(LLMOneri.olusturma_tarihi.desc()).all()

    return kayitlar