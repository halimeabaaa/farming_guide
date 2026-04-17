def bugun_onerilerini_uret(urun, toprak, hava: dict) -> list[dict]:
    oneriler = []

    urun_adi = (urun.urun_adi or "").lower()
    toprak_turu = (toprak.toprak_turu or "").lower()

    sicaklik_max = hava.get("sicaklik_max") or 0
    yagis_toplami = hava.get("yagis_toplami") or 0
    yagis_ihtimali_max = hava.get("yagis_ihtimali_max") or 0
    ruzgar_hizi_max = hava.get("ruzgar_hizi_max") or 0
    ortalama_nem = hava.get("ortalama_nem") or 0
    eto = hava.get("eto") or 0

    hassas_urunler = {"domates", "patates", "salatalik", "uzum", "biber"}

    if yagis_ihtimali_max >= 70 or yagis_toplami >= 5:
        oneriler.append({
            "oneri_turu": "sulama",
            "baslik": "Sulamayi ertele",
            "icerik": "Bugun / yarin yagis ihtimali yuksek gorunuyor. Ek sulama yapmadan once yagisi beklemeniz su tasarrufu ve kok sagligi acisindan daha uygun olabilir.",
            "risk_seviyesi": "orta"
        })

    if toprak_turu in {"killi", "tinli"} and (yagis_toplami >= 3 or yagis_ihtimali_max >= 60):
        oneriler.append({
            "oneri_turu": "toprak",
            "baslik": "Su birikmesi riski",
            "icerik": "Toprak yapiniz su tutmaya egilimli olabilir. Yagisli gunlerde asiri sulamadan kacin ve kok bolgesinde su birikmesi olup olmadigini kontrol edin.",
            "risk_seviyesi": "yuksek"
        })

    if sicaklik_max >= 32:
        oneriler.append({
            "oneri_turu": "sulama",
            "baslik": "Sulama saatini degistir",
            "icerik": "Maksimum sicaklik yuksek gorunuyor. Sulamayi ogle yerine sabah erken ya da aksam saatlerinde yapmak daha verimli olabilir.",
            "risk_seviyesi": "orta"
        })

    if ortalama_nem >= 80 and urun_adi in hassas_urunler:
        oneriler.append({
            "oneri_turu": "hastalik_riski",
            "baslik": "Mantar hastaligi riski",
            "icerik": f"{urun.urun_adi} icin yuksek nem kosullarinda mantar hastaligi riski artabilir. Yapraklarda leke, curume veya kuf benzeri belirtileri takip edin.",
            "risk_seviyesi": "yuksek"
        })

    if ruzgar_hizi_max >= 35:
        oneriler.append({
            "oneri_turu": "hava_uyarisi",
            "baslik": "Ilaclama icin uygun olmayabilir",
            "icerik": "Ruzgar hizinin yuksek olmasi bekleniyor. Ilaclama veya yapraktan uygulamalar suruklenme nedeniyle verimsiz olabilir.",
            "risk_seviyesi": "orta"
        })

    if eto >= 5 and yagis_toplami < 1:
        oneriler.append({
            "oneri_turu": "sulama",
            "baslik": "Su ihtiyaci artabilir",
            "icerik": "Bugunku buharlasma / terleme etkisi yuksek gorunuyor. Toprak nemini kontrol ederek kontrollu sulama planlamasi yapin.",
            "risk_seviyesi": "dusuk"
        })

    if not oneriler:
        oneriler.append({
            "oneri_turu": "genel",
            "baslik": "Bugun icin kritik risk gorunmuyor",
            "icerik": "Mevcut hava ve profil verilerine gore bugun icin belirgin bir risk tespit edilmedi. Rutininizi izleyip tarla gozlemini surdurun.",
            "risk_seviyesi": "dusuk"
        })

    return oneriler