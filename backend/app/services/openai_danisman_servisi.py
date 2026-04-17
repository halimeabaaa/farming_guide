from openai import OpenAI

from app.core.config import ayarlar
from app.prompts.openai_danisman_prompt import openai_danisman_promptu_olustur


class OpenAIDanismanHatasi(Exception):
    pass


def openai_danisman_cevabi_uret(
    profil: dict,
    urun: dict | None,
    toprak: dict | None,
    hava: dict | None,
    kural_onerileri: list[dict],
    kullanici_sorusu: str,
    resim_base64: str | None = None,
    resim_mime_turu: str | None = None
) -> str:
    if not ayarlar.OPENAI_API_KEY:
        raise OpenAIDanismanHatasi("OPENAI_API_KEY tanimli degil")

    try:
        client = OpenAI(api_key=ayarlar.OPENAI_API_KEY)

        prompt = openai_danisman_promptu_olustur(
            profil=profil,
            urun=urun,
            toprak=toprak,
            hava=hava,
            kural_onerileri=kural_onerileri,
            kullanici_sorusu=kullanici_sorusu
        )

        user_content = [
            {"type": "input_text", "text": prompt}
        ]

        if resim_base64 and resim_mime_turu:
            user_content.append({
                "type": "input_image",
                "image_url": f"data:{resim_mime_turu};base64,{resim_base64}"
            })

        response = client.responses.create(
            model=ayarlar.OPENAI_MODEL,
            instructions=(
                "Sen ust duzey bir tarim danismanisin. "
                "Yalnizca verilen veriye dayan, uydurma bilgi verme. "
                "Once kisa durum ozeti ver, sonra net aksiyon maddeleri yaz. "
                "Her oneri uygulanabilir, sahaya uygun ve zamanli olsun. "
                "Eger kullanici resim gonderdiyse gorseldeki belirtiyi mutlaka degerlendir. "
                "Belirsizlik varsa net sekilde belirt."
            ),
            input=[{
                "role": "user",
                "content": user_content
            }]
        )

        cevap = getattr(response, "output_text", None)
        if not cevap:
            raise OpenAIDanismanHatasi("Modelden bos cevap geldi")

        return cevap.strip()

    except OpenAIDanismanHatasi:
        raise
    except Exception as e:
        raise OpenAIDanismanHatasi(f"Danisman istegi hatasi: {type(e).__name__}: {str(e)}")