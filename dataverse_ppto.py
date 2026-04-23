"""
Extract and transform PPTO MENSUAL data from Dataverse (Common Data Service).

Mirrors the Power Query M pipeline:
  Dataverse → select columns → rename → MesTexto → filter ACUMULADO/TOTAL →
  filter categories with "T" → fecha_reporte
"""
import hashlib
import re

import duckdb
import msal
import pandas as pd
import requests
from cryptography import x509
from cryptography.hazmat.primitives import serialization

# ── Configuration ────────────────────────────────────────────────────────────
CLIENT_ID     = "b78cd209-e3e1-4c93-b17a-131823736792"
TENANT_ID     = "35f9d9b9-40d2-40b9-977b-83f5634f54da"
PEM_PATH      = "./CertificadoGrupoCars.pem"
DATAVERSE_URL = "https://grupocars-dev.crm4.dynamics.com"
ENTITY_NAME   = "cgib_pptomensuals"   # pluralised entity name in Dataverse API
SCOPES        = [f"{DATAVERSE_URL}/.default"]

# Columns to fetch from Dataverse (must use schema names)
DV_COLUMNS = [
    "cgib_concepto",
    "cgib_categoria",
    "cgib_totalbase",
    "cgib_empresa",
    "cgib_mes",
    "cgib_ano",
    "cgib_valorporcentaje",
]

MONTH_NAMES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}


# ── Certificate helpers (re-used from sharepoint_balance) ────────────────────

def _load_pem(pem_path: str) -> tuple[str, str]:
    """Return (private_key_pem, certificate_pem) extracted from a combined PEM file."""
    with open(pem_path) as f:
        content = f.read()
    pk = re.search(r"-----BEGIN PRIVATE KEY-----.*?-----END PRIVATE KEY-----", content, re.DOTALL).group()
    crt = re.search(r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----", content, re.DOTALL).group()
    return pk, crt


def _thumbprint(cert_pem: str) -> str:
    """Compute the SHA-1 thumbprint MSAL needs for certificate credentials."""
    cert = x509.load_pem_x509_certificate(cert_pem.encode())
    der = cert.public_bytes(serialization.Encoding.DER)
    return hashlib.sha1(der).hexdigest().upper()


# ── Authentication ───────────────────────────────────────────────────────────

def _get_token(client_id: str, tenant_id: str, pem_path: str) -> str:
    private_key, certificate = _load_pem(pem_path)
    app = msal.ConfidentialClientApplication(
        client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        client_credential={"thumbprint": _thumbprint(certificate), "private_key": private_key},
    )
    result = app.acquire_token_for_client(scopes=SCOPES)
    if "access_token" not in result:
        raise RuntimeError(f"Auth failed: {result.get('error_description', result)}")
    return result["access_token"]


# ── Dataverse API helpers ────────────────────────────────────────────────────

def _dv_get(token: str, url: str) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Accept": "application/json",
    }
    resp = requests.get(url, headers=headers, timeout=60)
    resp.raise_for_status()
    return resp.json()


def _fetch_all_records(token: str) -> list[dict]:
    """Fetch every record from the target entity handling Dataverse pagination."""
    select = ",".join(DV_COLUMNS)
    url = (
        f"{DATAVERSE_URL}/api/data/v9.2/{ENTITY_NAME}"
        f"?$select={select}"
    )
    records = []
    while url:
        data = _dv_get(token, url)
        records.extend(data.get("value", []))
        next_link = data.get("@odata.nextLink")
        url = next_link if next_link else None
    return records


# ── Data transformation ──────────────────────────────────────────────────────

def _transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply the Power Query M transformations in Python/pandas.
    """
    if df.empty:
        return df

    df = df.copy()

    # Rename columns (M: Table.RenameColumns)
    rename_map = {
        "cgib_categoria": "Categoria",
        "cgib_totalbase": "TotalBase",
        "cgib_valorporcentaje": "ValorPorcentaje",
        "cgib_empresa": "Empresa",
        "cgib_ano": "Año",
        "cgib_mes": "Mes",
        "cgib_concepto": "Concepto",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # Ensure Mes is string for text operations
    df["Mes"] = df["Mes"].astype(str)

    # MesTexto logic (M: Agregar MesTexto)
    def _mes_texto(row):
        mes_val = str(row["Mes"]).strip().upper()
        if mes_val in ("ACUMULADO", "TOTAL"):
            return "Total"
        try:
            mes_num = int(mes_val)
            return MONTH_NAMES_ES.get(mes_num, mes_val)
        except (ValueError, TypeError):
            return row["Mes"]

    df["MesTexto"] = df.apply(_mes_texto, axis=1)

    # Replace "MESACUMULADO" → "00" in Mes (M: Valor reemplazado6)
    df["Mes"] = df["Mes"].str.replace("MESACUMULADO", "00", regex=False)

    # Filter Mes <> "ACUMULADO" (M: Filas filtradas)
    df = df[df["Mes"].str.strip().str.upper() != "ACUMULADO"]

    # Replace "MESACUMULADO" → "Total" in MesTexto (M: Valor reemplazado7)
    df["MesTexto"] = df["MesTexto"].str.replace("MESACUMULADO", "Total", regex=False)

    # Filter categories that do NOT contain "T" (M: Filas filtradas1)
    df = df[~df["Categoria"].astype(str).str.contains("T", na=False)]

    # Filter MesTexto <> "Total" (M: Filas filtradas2)
    df = df[df["MesTexto"].str.strip().str.lower() != "total"]

    # fecha_reporte (M: Personalizada agregada)
    df["Año_num"] = pd.to_numeric(df["Año"], errors="coerce")
    df["Mes_num"] = pd.to_numeric(df["Mes"], errors="coerce")
    df["fecha_reporte"] = pd.to_datetime(
        df["Año_num"].astype("Int64").astype(str) + "-" +
        df["Mes_num"].astype("Int64").astype(str).str.zfill(2) + "-01",
        errors="coerce",
    ).dt.date

    # Clean up helper columns
    df = df.drop(columns=["Año_num", "Mes_num"], errors="ignore")

    return df


# ── Public API ───────────────────────────────────────────────────────────────

def fetch_ppto_mensual(
    client_id: str = CLIENT_ID,
    tenant_id: str = TENANT_ID,
    pem_path: str = PEM_PATH,
) -> pd.DataFrame:
    """
    Authenticate to Dataverse with the PEM certificate and return the transformed
    PPTO MENSUAL DataFrame, equivalent to the Power Query M pipeline output.
    """
    token = _get_token(client_id, tenant_id, pem_path)
    print("Fetching records from Dataverse...")
    records = _fetch_all_records(token)
    print(f"  {len(records):,} raw records fetched")

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    df = _transform(df)
    print(f"  {len(df):,} records after transformation")
    return df


# ── CLI entry point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    DB_PATH = "mazda.duckdb"
    TABLE_NAME = "ppto_mensual"

    print("Autenticando con Dataverse...")
    df = fetch_ppto_mensual()

    if df.empty:
        print("No se encontraron registros en cgib_pptomensual.")
    else:
        print(f"{len(df):,} filas · {len(df.columns)} columnas obtenidas")
        print(f"Cargando en {DB_PATH} → tabla '{TABLE_NAME}'...")

        con = duckdb.connect(DB_PATH)
        con.register("_ppto_df", df)
        con.execute(f"CREATE OR REPLACE TABLE {TABLE_NAME} AS SELECT * FROM _ppto_df")
        count = con.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]
        con.close()

        print(f"  Tabla '{TABLE_NAME}' creada con {count:,} filas.")
        print("Listo.")
