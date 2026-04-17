from app.schemas.ai_oneri import AIOneriAciklamaIstek


def ai_destekli_oneri_acikla(veri: AIOneriAciklamaIstek) -> dict:
    giris = []

    if veri.sehir:
        konum = veri.sehir
        if veri.ilce:
            konum = f"{veri.ilce}, {veri.sehir}"
        giris.append(f"{konum} bolgesindeki")
    else:
        giris.append("Bulundugunuz bolgedeki")

    if veri.urun_adi:
        giris.append(f"{veri.urun_adi} uretiminiz icin")

    hava_kisimi = []

    if veri.sicaklik_max is not None:
        hava_kisimi.append(f"maksimum sicaklik {veri.sicaklik_max}°C")
    if veri.yagis_ihtimali_max is not None:
        hava_kisimi.append(f"yagis ihtimali %{veri.yagis_ihtimali_max}")
    if veri.yagis_toplami is not None:
        hava_kisimi.append(f"toplam yagis {veri.yagis_toplami} mm")
    if veri.ruzgar_hizi_max is not None:
        hava_kisimi.append(f"ruzgar hizi {veri.ruzgar_hizi_max} km/s")
    if veri.ortalama_nem is not None:
        hava_kisimi.append(f"ortalama nem %{veri.ortalama_nem}")

    hava_metin = ""
    if hava_kisimi:
        hava_metin = "Bugunku hava verilerine gore " + ", ".join(hava_kisimi) + " seviyesinde gorunuyor. "

    toprak_metin = ""
    if veri.toprak_turu:
        toprak_metin = f"Toprak yapiniz {veri.toprak_turu} oldugu icin bu durum karar verirken dikkate alinmalidir. "

    risk_metin = ""
    if veri.risk_seviyesi == "yuksek":
        risk_metin = "Bu nedenle dikkatli hareket etmeniz onemlidir. "
    elif veri.risk_seviyesi == "orta":
        risk_metin = "Bu durum orta duzeyde bir dikkat gerektirir. "
    elif veri.risk_seviyesi == "dusuk":
        risk_metin = "Bu durum dusuk riskli gorunmektedir. "

    aciklama = (
        f"{' '.join(giris)} {veri.baslik.lower()} onerilmektedir. "
        f"{hava_metin}"
        f"{toprak_metin}"
        f"{veri.icerik} "
        f"{risk_metin}"
        f"Lutfen tarladaki guncel durumu gozlemleyerek bu oneriyi uygulayin."
    )

    aciklama = " ".join(aciklama.split())

    return {
        "baslik": veri.baslik,
        "aciklama": aciklama,
        "risk_seviyesi": veri.risk_seviyesi,
        "oneri_turu": veri.oneri_turu
    }