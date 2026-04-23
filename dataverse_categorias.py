"""
Extract cgib_categorias from Dataverse using certificate (PEM) authentication.

Mirrors the Power Query M pipeline:
  Dataverse → cgib_categorias → select columns → add Nombre column → load to DuckDB
"""
import duckdb
import pandas as pd
import requests

from sharepoint_balance import (
    CLIENT_ID,
    TENANT_ID,
    PEM_PATH,
    _get_token,
)

# ── Configuration ────────────────────────────────────────────────────────────
DATAVERSE_HOST  = "grupocars-dev.crm4.dynamics.com"
DATAVERSE_URL   = f"https://{DATAVERSE_HOST}"
DATAVERSE_SCOPE = [f"{DATAVERSE_URL}/.default"]
API_BASE        = f"{DATAVERSE_URL}/api/data/v9.2"
ENTITY_SET      = "cgib_categoriases"
SELECT_COLS     = "cgib_categoriasid,cgib_name,cgib_identificador"


# ── Dataverse helpers ─────────────────────────────────────────────────────────

def _get_dataverse_token() -> str:
    return _get_token(CLIENT_ID, TENANT_ID, PEM_PATH, scopes=DATAVERSE_SCOPE)


def _dataverse_get(token: str, entity_set: str, select: str = None) -> list[dict]:
    """Fetch all pages from a Dataverse OData endpoint."""
    headers = {
        "Authorization":    f"Bearer {token}",
        "Accept":           "application/json",
        "OData-MaxVersion": "4.0",
        "OData-Version":    "4.0",
        "Prefer":           "odata.maxpagesize=5000",
    }
    url = f"{API_BASE}/{entity_set}"
    params = {}
    if select:
        params["$select"] = select

    records = []
    while url:
        resp = requests.get(url, headers=headers, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        records.extend(data.get("value", []))
        url    = data.get("@odata.nextLink")
        params = {}  # nextLink already contains params
    return records


# ── Transform ─────────────────────────────────────────────────────────────────

def _transform(records: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(records)

    # Drop OData metadata column if present
    df = df.drop(columns=[c for c in df.columns if c.startswith("@")], errors="ignore")

    # Keep only the columns we need, then drop the ID
    for col in ("cgib_categoriasid", "cgib_name", "cgib_identificador"):
        if col not in df.columns:
            df[col] = pd.NA

    df = df[["cgib_name", "cgib_identificador"]]

    # Nombre = cgib_identificador + " " + cgib_name  (mirrors M's Text.From concatenation)
    df["Nombre"] = (
        df["cgib_identificador"].astype(str).where(df["cgib_identificador"].notna(), "")
        + " "
        + df["cgib_name"].astype(str).where(df["cgib_name"].notna(), "")
    ).str.strip()

    return df


# ── Public API ────────────────────────────────────────────────────────────────

def fetch_categorias() -> pd.DataFrame:
    """
    Authenticate to Dataverse and return the cgib_categorias DataFrame.

    Returns
    -------
    pd.DataFrame with columns: cgib_name, cgib_identificador, Nombre
    """
    token   = _get_dataverse_token()
    records = _dataverse_get(token, ENTITY_SET, select=SELECT_COLS)
    return _transform(records)


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    DB_PATH    = "mazda.duckdb"
    TABLE_NAME = "categorias"

    print("Autenticando con Dataverse...")
    df = fetch_categorias()

    if df.empty:
        print("No se encontraron registros en cgib_categorias.")
    else:
        print(f"  {len(df):,} filas · {len(df.columns)} columnas obtenidas")
        print(f"Cargando en {DB_PATH} → tabla '{TABLE_NAME}'...")

        con = duckdb.connect(DB_PATH)
        con.register("_categorias_df", df)
        con.execute(f"CREATE OR REPLACE TABLE {TABLE_NAME} AS SELECT * FROM _categorias_df")
        count = con.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]
        con.close()

        print(f"  Tabla '{TABLE_NAME}' creada con {count:,} filas.")
        print("Listo.")
