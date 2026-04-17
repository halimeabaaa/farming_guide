from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import ayarlar

engine = create_engine(
    ayarlar.DATABASE_URL,
    echo=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def veritabani_al():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()