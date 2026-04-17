import requests


class HavaServisiHatasi(Exception):
    pass


def turkce_karakterleri_duzelt(metin: str) -> str:
    if not metin:
        return metin

    ceviri = str.maketrans({
        "ç": "c",
        "Ç": "C",
        "ğ": "g",
        "Ğ": "G",
        "ı": "i",
        "İ": "I",
        "ö": "o",
        "Ö": "O",
        "ş": "s",
        "Ş": "S",
        "ü": "u",
        "Ü": "U",
    })
    return metin.translate(ceviri)


def metni_temizle(metin: str | None) -> str | None:
    if metin is None:
        return None

    temiz = " ".join(metin.strip().split())
    return temiz if temiz else None


def geocoding_istegi(arama_metni: str, ulke_kodu: str | None = "TR") -> list:
    params = {
        "name": arama_metni,
        "count": 10,
        "language": "tr",
        "format": "json"
    }

    if ulke_kodu:
        params["countryCode"] = ulke_kodu

    try:
        response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params=params,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except requests.RequestException as e:
        raise HavaServisiHatasi(f"Geocoding servisine baglanilamadi: {str(e)}")


def konum_bul(sehir: str, ilce: str | None = None) -> dict:
    sehir = metni_temizle(sehir)
    ilce = metni_temizle(ilce)

    if not sehir:
        raise HavaServisiHatasi("Sehir bilgisi bos olamaz")

    aramalar = []

    if ilce:
        aramalar.extend([
            f"{ilce}, {sehir}",
            f"{ilce} {sehir}",
            f"{turkce_karakterleri_duzelt(ilce)}, {turkce_karakterleri_duzelt(sehir)}",
            f"{turkce_karakterleri_duzelt(ilce)} {turkce_karakterleri_duzelt(sehir)}",
        ])

    aramalar.extend([
        sehir,
        turkce_karakterleri_duzelt(sehir)
    ])

    denenmisler = set()

    for arama in aramalar:
        if not arama or arama in denenmisler:
            continue

        denenmisler.add(arama)

        # Önce Türkiye filtreli ara
        sonuclar = geocoding_istegi(arama, ulke_kodu="TR")
        if sonuclar:
            return sonuclar[0]

        # Sonra ülke filtresi olmadan dene
        sonuclar = geocoding_istegi(arama, ulke_kodu=None)
        if sonuclar:
            return sonuclar[0]

    raise HavaServisiHatasi(
        f"Sehir / ilce bilgisine gore konum bulunamadi. Denenen aramalar: {list(denenmisler)}"
    )


def bugun_hava_getir(sehir: str, ilce: str | None = None) -> dict:
    konum = konum_bul(sehir=sehir, ilce=ilce)

    try:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": konum["latitude"],
                "longitude": konum["longitude"],
                "timezone": "auto",
                "forecast_days": 1,
                "daily": ",".join([
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_sum",
                    "precipitation_probability_max",
                    "wind_speed_10m_max",
                    "et0_fao_evapotranspiration"
                ])
            },
            timeout=15
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        raise HavaServisiHatasi(f"Hava durumu servisine baglanilamadi: {str(e)}")

    daily = data.get("daily", {})
    if not daily or not daily.get("time"):
        raise HavaServisiHatasi("Hava verisi alinamadi")

    return {
        "sehir": sehir,
        "ilce": ilce,
        "enlem": float(konum["latitude"]),
        "boylam": float(konum["longitude"]),
        "zaman_dilimi": data.get("timezone", "auto"),
        "tarih": daily["time"][0],
        "sicaklik_max": daily.get("temperature_2m_max", [None])[0],
        "sicaklik_min": daily.get("temperature_2m_min", [None])[0],
        "yagis_toplami": daily.get("precipitation_sum", [None])[0],
        "yagis_ihtimali_max": daily.get("precipitation_probability_max", [None])[0],
        "ruzgar_hizi_max": daily.get("wind_speed_10m_max", [None])[0],
        "ortalama_nem": None,
        "eto": daily.get("et0_fao_evapotranspiration", [None])[0],
    }