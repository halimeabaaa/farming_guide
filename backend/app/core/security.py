from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import ayarlar

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def sifre_dogrula(duz_sifre: str, hashlenmis_sifre: str) -> bool:
    return pwd_context.verify(duz_sifre, hashlenmis_sifre)


def sifre_hashle(sifre: str) -> str:
    return pwd_context.hash(sifre)


def access_token_olustur(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ayarlar.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, ayarlar.SECRET_KEY, algorithm=ayarlar.ALGORITHM)
    return encoded_jwt