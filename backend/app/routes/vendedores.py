"""Vendedores API routes."""
import math
from typing import Optional
import pandas as pd
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.auth import get_current_user
from app.services import queries


def _clean_nan(obj):
    """Recursively replace NaN with None for JSON serialization."""
    if isinstance(obj, dict):
        return {k: _clean_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean_nan(v) for v in obj]
    if isinstance(obj, float) and math.isnan(obj):
        return None
    return obj

router = APIRouter()


class VendedoresResponse(BaseModel):
    rows: list[dict]
    totales: dict


class VentasTipoResponse(BaseModel):
    rows: list[dict]


@router.get("/años")
def get_años(current_user: str = Depends(get_current_user)):
    return {"años": queries.obtener_años_disponibles()}


@router.get("/resumen")
def get_resumen(
    anio: Optional[int] = Query(None),
    mes: Optional[int] = Query(None),
    current_user: str = Depends(get_current_user),
):
    con = queries.get_connection()
    try:
        df = queries.resumen_vendedores_filtrado(con, anio, mes)
        if df.empty:
            return {"rows": [], "totales": {}}

        columnas_ordenadas = [
            "vendedor", "con_placa", "subidos", "pendientes", "pedidos", "ventas",
            "suma_bb1", "media_bb1", "suma_bb2", "media_bb2", "suma_bb3", "media_bb3",
            "media_descuento_pct", "operaciones_financiadas",
        ]
        df = df[columnas_ordenadas]

        totales = {
            "vendedor": "TOTALES",
            "con_placa": int(df["con_placa"].sum()),
            "subidos": int(df["subidos"].sum()),
            "pendientes": int(df["pendientes"].sum()),
            "pedidos": int(df["pedidos"].sum()),
            "ventas": int(df["ventas"].sum()),
            "suma_bb1": round(float(df["suma_bb1"].sum()), 2),
            "media_bb1": round(float(df["media_bb1"].mean()), 2),
            "suma_bb2": round(float(df["suma_bb2"].sum()), 2),
            "media_bb2": round(float(df["media_bb2"].mean()), 2),
            "suma_bb3": round(float(df["suma_bb3"].sum()), 2),
            "media_bb3": round(float(df["media_bb3"].mean()), 2),
            "media_descuento_pct": round(float(df["media_descuento_pct"].mean()), 2),
            "operaciones_financiadas": int(df["operaciones_financiadas"].sum()),
        }

        records = df.replace({float('nan'): None}).to_dict("records")
        records.append(totales)

        return _clean_nan({"rows": records, "totales": totales})
    finally:
        con.close()


@router.get("/ventas-por-tipo")
def get_ventas_por_tipo(
    anio: Optional[int] = Query(None),
    mes: Optional[int] = Query(None),
    current_user: str = Depends(get_current_user),
):
    con = queries.get_connection()
    try:
        df = queries.ventas_por_vendedor_tipo(con, anio, mes)
        if df.empty:
            return {"rows": []}

        df_pivot = df.pivot(index="vendedor", columns="tipo_venta", values="cantidad")
        df_pivot = df_pivot.fillna(0).astype(int)
        df_pivot["TOTAL"] = df_pivot.sum(axis=1)
        df_pivot = df_pivot.sort_values("TOTAL", ascending=False)

        totales = df_pivot.sum(axis=0)
        totales.name = "TOTALES"
        df_pivot = pd.concat([df_pivot, totales.to_frame().T])
        df_pivot = df_pivot.reset_index()
        df_pivot.columns.name = None
        df_pivot = df_pivot.rename(columns={"index": "Vendedor"})

        records = df_pivot.replace({float('nan'): None}).to_dict("records")
        return _clean_nan({"rows": records})
    finally:
        con.close()
