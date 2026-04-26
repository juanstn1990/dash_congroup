"""Balance P&G API routes."""
import io
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.auth import get_current_user
from app.services import balance_service as bs

router = APIRouter()


class FilterOptionsResponse(BaseModel):
    empresas: list[str]
    años: list[int]


@router.get("/filters")
def get_filters(current_user: str = Depends(get_current_user)):
    empresas, años = bs.get_filter_options()
    return {"empresas": empresas, "años": años}


@router.get("/resultado")
def get_resultado(
    empresa: str = Query("Todas"),
    año: str = Query("Todos"),
    current_user: str = Depends(get_current_user),
):
    return bs.get_balance_data(empresa, año)


@router.get("/presupuesto")
def get_presupuesto(
    empresa: str = Query("Todas"),
    año: str = Query("Todos"),
    current_user: str = Depends(get_current_user),
):
    return bs.get_ppto_data(empresa, año)


@router.get("/vs-presupuesto")
def get_vs_presupuesto(
    empresa: str = Query("Todas"),
    año: str = Query("Todos"),
    current_user: str = Depends(get_current_user),
):
    return bs.get_vs_ppto_data(empresa, año)


@router.get("/vs-anterior")
def get_vs_anterior(
    empresa: str = Query("Todas"),
    año: str = Query("Todos"),
    mes: int = Query(1),
    current_user: str = Depends(get_current_user),
):
    return bs.get_vs_anterior_data(empresa, año, mes)


@router.get("/cuentas")
def get_cuentas(
    empresa: str = Query("Todas"),
    año: str = Query("Todos"),
    categoria: str = Query(...),
    current_user: str = Depends(get_current_user),
):
    return bs.get_cuentas_data(empresa, año, categoria)


@router.get("/export-excel")
def export_excel(
    empresa: str = Query("Todas"),
    año: str = Query("Todos"),
    current_user: str = Depends(get_current_user),
):
    xlsx_bytes = bs.build_excel_bytes(empresa, año)
    if xlsx_bytes is None:
        return {"error": "No hay datos para exportar"}
    return StreamingResponse(
        io.BytesIO(xlsx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="balance_pyg.xlsx"'},
    )
