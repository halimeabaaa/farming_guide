from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import veritabani_al
from app.core.dependencies import aktif_kullanici_getir
from app.models.kullanici import Kullanici
from app.schemas.dashboard import DashboardOzetCikti
from app.services.dashboard_servisi import (
    dashboard_ozet_getir,
    dashboard_yenile,
    DashboardHatasi
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/ozet", response_model=DashboardOzetCikti)
def dashboard_ozet(
    db: Session = Depends(veritabani_al),
    aktif_kullanici: Kullanici = Depends(aktif_kullanici_getir)
):
    try:
        return dashboard_ozet_getir(db, aktif_kullanici.id)
    except DashboardHatasi as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/yenile", response_model=DashboardOzetCikti)
def dashboard_yenile_endpoint(
    db: Session = Depends(veritabani_al),
    aktif_kullanici: Kullanici = Depends(aktif_kullanici_getir)
):
    try:
        return dashboard_yenile(db, aktif_kullanici.id)
    except DashboardHatasi as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )