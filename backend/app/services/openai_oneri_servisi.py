import json
from openai import OpenAI

from app.core.config import ayarlar
from app.prompts.openai_oneri_prompt import openai_tarim_oneri_promptu_olustur
from app.schemas.llm_oneri import LLMOneriCikti


class OpenAIOneriHatasi(Exception):
    pass


def openai_schema_olustur() -> dict:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "genel_durum": {
                "type": "string"
            },
            "ozet": {
                "type": "string"
            },
            "oncelik_puani": {
                "type": "integer"
            },
            "maddeler": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "baslik": {"type": "string"},
                        "aciklama": {"type": "string"},
                        "oneri_turu": {"type": "string"},
                        "risk_seviyesi": {"type": "string"},
                        "uygulanacak_aksiyon": {"type": "string"},
                    },
                    "required": [
                        "baslik",
                        "aciklama",
                        "oneri_turu",
                        "risk_seviyesi",
                        "uygulanacak_aksiyon"
                    ]
                }
            },
            "ciftciye_not": {
                "type": "string"
            }
        },
        "required": [
            "genel_durum",
            "ozet",
            "oncelik_puani",
            "maddeler",
            "ciftciye_not"
        ]
    }


def openai_tarim_onerisi_uret(
    profil: dict,
    urun: dict,
    toprak: dict,
    hava: dict,
    kural_tabanli_oneriler: list[dict]
) -> LLMOneriCikti:
    if not ayarlar.OPENAI_API_KEY:
        raise OpenAIOneriHatasi("OPENAI_API_KEY tanimli degil")

    try:
        client = OpenAI(api_key=ayarlar.OPENAI_API_KEY)

        prompt = openai_tarim_oneri_promptu_olustur(
            profil=profil,
            urun=urun,
            toprak=toprak,
            hava=hava,
            kural_tabanli_oneriler=kural_tabanli_oneriler
        )

        schema = openai_schema_olustur()

        response = client.responses.create(
            model=ayarlar.OPENAI_MODEL,
            instructions=(
                "Sen tarimsal karar destek amacli calisan dikkatli bir asistansin. "
                "Yalnizca verilen veriye dayan. Uydurma bilgi verme. "
                "Cevabi verilen JSON schema'ya kesinlikle uydur."
            ),
            input=prompt,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "tarim_oneri",
                    "strict": True,
                    "schema": schema
                }
            }
        )

        raw_text = getattr(response, "output_text", None)
        if not raw_text:
            raise OpenAIOneriHatasi(f"Modelden bos cevap geldi. Ham response: {response}")

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError as e:
            raise OpenAIOneriHatasi(f"JSON parse hatasi: {str(e)} | raw_text={raw_text}")

        try:
            return LLMOneriCikti(**parsed)
        except Exception as e:
            raise OpenAIOneriHatasi(f"Schema dogrulama hatasi: {str(e)} | parsed={parsed}")

    except OpenAIOneriHatasi:
        raise
    except Exception as e:
        raise OpenAIOneriHatasi(f"OpenAI istegi hatasi: {type(e).__name__}: {str(e)}")