from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.ciftci_profili import CiftciProfili
from app.models.urun import Urun
from app.models.toprak_bilgisi import ToprakBilgisi
from app.models.oneri import Oneri
from app.models.hava_kaydi import HavaKaydi
from app.services.hava_servisi import bugun_hava_getir, HavaServisiHatasi
from app.services.kural_motoru import bugun_onerilerini_uret
from app.services.ai_aciklama_servisi import ai_destekli_oneri_acikla
from app.schemas.ai_oneri import AIOneriAciklamaIstek


class DashboardHatasi(Exception):
    pass


def profili_getir(db: Session, kullanici_id: int):
    profil = db.query(CiftciProfili).filter(
        CiftciProfili.kullanici_id == kullanici_id
    ).first()

    if not profil:
        raise DashboardHatasi("Once ciftci profili olusturmaniz gerekiyor")

    return profil


def urunleri_getir(db: Session, profil_id: int):
    return db.query(Urun).filter(
        Urun.ciftci_profil_id == profil_id
    ).order_by(Urun.id.desc()).all()


def aktif_urunu_getir(db: Session, profil_id: int):
    return db.query(Urun).filter(
        Urun.ciftci_profil_id == profil_id
    ).order_by(Urun.id.desc()).first()


def topragi_getir(db: Session, profil_id: int):
    return db.query(ToprakBilgisi).filter(
        ToprakBilgisi.ciftci_profil_id == profil_id
    ).first()


def bugunku_onerileri_getir(db: Session, profil_id: int):
    return db.query(Oneri).filter(
        Oneri.ciftci_profil_id == profil_id,
        func.date(Oneri.olusturma_tarihi) == date.today()
    ).order_by(Oneri.id.asc()).all()


def hava_kaydini_guncelle_veya_ekle(db: Session, hava: dict):
    mevcut = db.query(HavaKaydi).filter(
        HavaKaydi.sehir == hava["sehir"],
        HavaKaydi.ilce == hava["ilce"],
        HavaKaydi.kayit_tarihi == hava["tarih"]
    ).first()

    if mevcut:
        mevcut.sicaklik = hava["sicaklik_max"]
        mevcut.nem = hava["ortalama_nem"]
        mevcut.yagis_miktari = hava["yagis_toplami"]
        mevcut.ruzgar_hizi = hava["ruzgar_hizi_max"]
        mevcut.hava_aciklamasi = "Gunluk tahmin"
    else:
        yeni_kayit = HavaKaydi(
            sehir=hava["sehir"],
            ilce=hava["ilce"],
            kayit_tarihi=hava["tarih"],
            sicaklik=hava["sicaklik_max"],
            nem=hava["ortalama_nem"],
            yagis_miktari=hava["yagis_toplami"],
            ruzgar_hizi=hava["ruzgar_hizi_max"],
            hava_aciklamasi="Gunluk tahmin"
        )
        db.add(yeni_kayit)

    db.commit()


def bugunku_onerileri_yenile(db: Session, profil, urunler: list, toprak, hava: dict):
    eski_oneriler = db.query(Oneri).filter(
        Oneri.ciftci_profil_id == profil.id,
        func.date(Oneri.olusturma_tarihi) == date.today()
    ).all()

    for eski in eski_oneriler:
        db.delete(eski)

    db.commit()

    for urun in urunler:
        urun_onerileri = bugun_onerilerini_uret(
            urun=urun,
            toprak=toprak,
            hava=hava
        )

        for oneri_dict in urun_onerileri:
            kayit = Oneri(
                ciftci_profil_id=profil.id,
                urun_id=urun.id,
                oneri_turu=oneri_dict["oneri_turu"],
                baslik=f"[{urun.urun_adi}] {oneri_dict['baslik']}",
                icerik=oneri_dict["icerik"],
                risk_seviyesi=oneri_dict["risk_seviyesi"]
            )
            db.add(kayit)

    db.commit()

    return bugunku_onerileri_getir(db, profil.id)


def ai_onerileri_hazirla(profil, urunler: list, toprak, hava: dict, bugunku_oneriler: list):
    sonuc = []
    urun_id_haritasi = {u.id: u for u in urunler}

    for oneri in bugunku_oneriler:
        oneri_urunu = urun_id_haritasi.get(oneri.urun_id)
        urun_adi = oneri_urunu.urun_adi if oneri_urunu else "Urun"

        istek = AIOneriAciklamaIstek(
            urun_adi=urun_adi,
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


def dashboard_ozet_getir(db: Session, kullanici_id: int):
    profil = profili_getir(db, kullanici_id)
    urunler = urunleri_getir(db, profil.id)
    aktif_urun = aktif_urunu_getir(db, profil.id)
    toprak = topragi_getir(db, profil.id)

    hava = None
    bugunku_oneriler = bugunku_onerileri_getir(db, profil.id)
    ai_oneriler = []

    try:
        hava = bugun_hava_getir(sehir=profil.sehir, ilce=profil.ilce)
    except HavaServisiHatasi:
        hava = None

    if hava and urunler and toprak and bugunku_oneriler:
        ai_oneriler = ai_onerileri_hazirla(
            profil=profil,
            urunler=urunler,
            toprak=toprak,
            hava=hava,
            bugunku_oneriler=bugunku_oneriler
        )

    return {
        "profil": profil,
        "urunler": urunler,
        "aktif_urun": aktif_urun,
        "toprak": toprak,
        "hava": hava,
        "bugunku_oneriler": bugunku_oneriler,
        "ai_oneriler": ai_oneriler
    }


def dashboard_yenile(db: Session, kullanici_id: int):
    profil = profili_getir(db, kullanici_id)

    urunler = urunleri_getir(db, profil.id)
    aktif_urun = aktif_urunu_getir(db, profil.id)
    if not urunler:
        raise DashboardHatasi("Once en az bir urun eklemeniz gerekiyor")

    toprak = topragi_getir(db, profil.id)
    if not toprak:
        raise DashboardHatasi("Once toprak bilgisi eklemeniz gerekiyor")

    try:
        hava = bugun_hava_getir(sehir=profil.sehir, ilce=profil.ilce)
    except HavaServisiHatasi as e:
        raise DashboardHatasi(str(e))

    hava_kaydini_guncelle_veya_ekle(db, hava)

    bugunku_oneriler = bugunku_onerileri_yenile(
        db=db,
        profil=profil,
        urunler=urunler,
        toprak=toprak,
        hava=hava
    )

    ai_oneriler = ai_onerileri_hazirla(
        profil=profil,
        urunler=urunler,
        toprak=toprak,
        hava=hava,
        bugunku_oneriler=bugunku_oneriler
    )

    return {
        "profil": profil,
        "urunler": urunler,
        "aktif_urun": aktif_urun,
        "toprak": toprak,
        "hava": hava,
        "bugunku_oneriler": bugunku_oneriler,
        "ai_oneriler": ai_oneriler
    }