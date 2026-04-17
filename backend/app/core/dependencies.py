from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import ayarlar
from app.core.database import veritabani_al
from app.models.kullanici import Kullanici
from app.schemas.token import TokenVerisi

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/kimlik/giris-yap")


def aktif_kullanici_getir(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(veritabani_al)
):
    kimlik_hatasi = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik bilgileri dogrulanamadi",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, ayarlar.SECRET_KEY, algorithms=[ayarlar.ALGORITHM])
        eposta: str = payload.get("sub")
        if eposta is None:
            raise kimlik_hatasi
        token_verisi = TokenVerisi(eposta=eposta)
    except JWTError:
        raise kimlik_hatasi

    kullanici = db.query(Kullanici).filter(Kullanici.eposta == token_verisi.eposta).first()
    if kullanici is None:
        raise kimlik_hatasi

    return kullanici