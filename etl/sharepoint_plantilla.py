"""
Extract PLANTILLA RESULTADO from SharePoint using certificate (PEM) authentication.

Mirrors the Power Query M pipeline:
  SharePoint files → filter BALANCE/Plantilla Resultado/ → read Plantilla Resultado.xlsx
  → Hoja1 → promote headers → cast types → load to DuckDB
"""
import io

import duckdb
import pandas as pd
import requests

from sharepoint_balance import (
    CLIENT_ID,
    TENANT_ID,
    PEM_PATH,
    GRAPH_SCOPES,
    _get_token,
    _get_site_id,
    _graph_get,
)

# ── Configuration ────────────────────────────────────────────────────────────
PLANTILLA_FOLDER = "BALANCE/Plantilla Resultado"
PLANTILLA_FILE   = "Plantilla Resultado.xlsx"
SHEET_NAME       = "Hoja1"

COLUMN_TYPES = {
    "N":          "Int64",
    "Concepto":   "string",
    "Categoria":  "string",
    "GrupoPadre": "string",
    "Porcentaje": "string",
}


# ── Data helpers ─────────────────────────────────────────────────────────────

def _get_file_url(token: str, site_id: str) -> str:
    endpoint = f"/sites/{site_id}/drive/root:/{PLANTILLA_FOLDER}/{PLANTILLA_FILE}"
    data = _graph_get(token, endpoint)
    return data["@microsoft.graph.downloadUrl"]


def _read_sheet(download_url: str) -> pd.DataFrame:
    resp = requests.get(download_url, timeout=60)
    resp.raise_for_status()
    df = pd.read_excel(io.BytesIO(resp.content), sheet_name=SHEET_NAME, header=0)
    return df


def _apply_types(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col, dtype in COLUMN_TYPES.items():
        if col not in df.columns:
            continue
        if dtype == "Int64":
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
        else:
            df[col] = df[col].astype(str).where(df[col].notna(), pd.NA)
    return df


# ── Public API ───────────────────────────────────────────────────────────────

def fetch_plantilla(
    client_id: str = CLIENT_ID,
    tenant_id: str = TENANT_ID,
    pem_path:  str = PEM_PATH,
) -> pd.DataFrame:
    """
    Authenticate to SharePoint and return the Plantilla Resultado DataFrame.

    Returns
    -------
    pd.DataFrame with columns: N, Concepto, Categoria, GrupoPadre, Porcentaje
    (plus any extra columns present in Hoja1).
    """
    token        = _get_token(client_id, tenant_id, pem_path)
    site_id      = _get_site_id(token)
    download_url = _get_file_url(token, site_id)
    df           = _read_sheet(download_url)
    return _apply_types(df)


# ── CLI entry point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    DB_PATH    = "mazda.duckdb"
    TABLE_NAME = "plantilla_resultado"

    print("Autenticando con SharePoint...")
    df = fetch_plantilla()

    if df.empty:
        print("El archivo Plantilla Resultado.xlsx / Hoja1 está vacío.")
    else:
        print(f"  {len(df):,} filas · {len(df.columns)} columnas obtenidas")
        print(f"Cargando en {DB_PATH} → tabla '{TABLE_NAME}'...")

        con = duckdb.connect(DB_PATH)
        con.register("_plantilla_df", df)
        con.execute(f"CREATE OR REPLACE TABLE {TABLE_NAME} AS SELECT * FROM _plantilla_df")
        count = con.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]
        con.close()

        print(f"  Tabla '{TABLE_NAME}' creada con {count:,} filas.")
        print("Listo.")
