"""
Extract and transform BALANCE data from SharePoint using certificate (PEM) authentication.

Mirrors the Power Query M pipeline:
  SharePoint files → filter BALANCE/Detalle → read Excel → split filename →
  map empresa names → extract Mes/Año → fecha_reporte → concatenado_2
"""
import hashlib
import io
import re

import duckdb
import msal
import pandas as pd
import requests
from cryptography import x509
from cryptography.hazmat.primitives import serialization

# ── Configuration ────────────────────────────────────────────────────────────
CLIENT_ID      = "b78cd209-e3e1-4c93-b17a-131823736792"
TENANT_ID      = "35f9d9b9-40d2-40b9-977b-83f5634f54da"
PEM_PATH       = "./CertificadoGrupoCars.pem"
SITE_HOST      = "congroupiberiacsp.sharepoint.com"
SITE_PATH      = "/sites/grupocars"
BALANCE_FOLDER = "BALANCE/Detalle"
GRAPH_SCOPES   = ["https://graph.microsoft.com/.default"]

EMPRESA_MAP = {
    "BalanceKuroba": "KUROBA MOTOR SL",
    "BalanceMotorN": "MOTOR NACIENTE SL",
    "BalanceCars":   "CARS COREA SL",
    "BalanceAlbion": "ALBION MOTOR SL",
    "BalanceCanton": "CANTON MOTOR",
    "BalanceShin":   "SHINKANSEN",
}

MONTH_NAMES = {
    1: "ENERO",    2: "FEBRERO",   3: "MARZO",    4: "ABRIL",
    5: "MAYO",     6: "JUNIO",     7: "JULIO",    8: "AGOSTO",
    9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE",
}


# ── Certificate helpers ──────────────────────────────────────────────────────

def _load_pem(pem_path: str) -> tuple[str, str]:
    """Return (private_key_pem, certificate_pem) extracted from a combined PEM file."""
    with open(pem_path) as f:
        content = f.read()
    pk  = re.search(r"-----BEGIN PRIVATE KEY-----.*?-----END PRIVATE KEY-----",  content, re.DOTALL).group()
    crt = re.search(r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----",  content, re.DOTALL).group()
    return pk, crt


def _thumbprint(cert_pem: str) -> str:
    """Compute the SHA-1 thumbprint MSAL needs for certificate credentials."""
    cert = x509.load_pem_x509_certificate(cert_pem.encode())
    der  = cert.public_bytes(serialization.Encoding.DER)
    return hashlib.sha1(der).hexdigest().upper()


# ── Authentication & Graph helpers ──────────────────────────────────────────

def _get_token(client_id: str, tenant_id: str, pem_path: str, scopes: list[str] = None) -> str:
    private_key, certificate = _load_pem(pem_path)
    app = msal.ConfidentialClientApplication(
        client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        client_credential={"thumbprint": _thumbprint(certificate), "private_key": private_key},
    )
    result = app.acquire_token_for_client(scopes=scopes or GRAPH_SCOPES)
    if "access_token" not in result:
        raise RuntimeError(f"Auth failed: {result.get('error_description', result)}")
    return result["access_token"]


def _graph_get(token: str, endpoint: str, **kwargs) -> dict:
    url = f"https://graph.microsoft.com/v1.0{endpoint}"
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, **kwargs)
    resp.raise_for_status()
    return resp.json()


def _get_site_id(token: str) -> str:
    data = _graph_get(token, f"/sites/{SITE_HOST}:{SITE_PATH}")
    return data["id"]


def _list_balance_files(token: str, site_id: str) -> list[dict]:
    """Return [{name, download_url}] for all non-hidden files in BALANCE/Detalle."""
    endpoint = f"/sites/{site_id}/drive/root:/{BALANCE_FOLDER}:/children"
    files = []
    while endpoint:
        data = _graph_get(token, endpoint)
        for item in data.get("value", []):
            hidden = item.get("file") and item.get("fileSystemInfo", {}).get("attributes", "").lower().find("hidden") == -1
            if item.get("file") and not item.get("hidden", False):
                files.append({
                    "name":         item["name"],
                    "download_url": item["@microsoft.graph.downloadUrl"],
                })
        # Handle pagination
        endpoint = data.get("@odata.nextLink", "").replace("https://graph.microsoft.com/v1.0", "") or None
    return files


# ── Data transformation ──────────────────────────────────────────────────────

def _read_excel(download_url: str) -> pd.DataFrame:
    resp = requests.get(download_url, timeout=60)
    resp.raise_for_status()
    return pd.read_excel(io.BytesIO(resp.content))


def _transform(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    """
    Apply the Power Query M transformations to a single file's DataFrame.

    Filename convention: {Empresa}_{Fecha}_{suffix}.xlsx
    Fecha format: chars[2:4] = month (2 digits), chars[-4:] = year (4 digits)
    e.g. "BalanceCars_MM012025_v1.xlsx"
    """
    stem  = re.sub(r"\.xlsx?$", "", filename, flags=re.IGNORECASE)
    parts = stem.split("_", 2)            # max 3 parts like Power Query

    empresa_code = parts[0] if len(parts) > 0 else ""
    fecha        = parts[1] if len(parts) > 1 else ""
    # parts[2] (Source.Name.3) is discarded, same as M script

    df = df.copy()
    df["Source.Name"]    = filename
    df["Empresa"]        = empresa_code
    df["Fecha"]          = fecha
    df["Empresa Nombre"] = df["Empresa"].map(lambda e: EMPRESA_MAP.get(e, e))

    # Text.Middle(Fecha, 2, 2) → Python: Fecha[2:4]
    df["Mes"] = pd.to_numeric(df["Fecha"].str[2:4], errors="coerce").astype("Int64")
    # Text.End(Fecha, 4) → Python: Fecha[-4:]
    df["Año"] = pd.to_numeric(df["Fecha"].str[-4:], errors="coerce").astype("Int64")

    df["Nombre Mes"] = df["Mes"].map(MONTH_NAMES)

    if "Saldo Mensual" in df.columns:
        df["Saldo Mensual"] = pd.to_numeric(df["Saldo Mensual"], errors="coerce")

    df["fecha_reporte"] = pd.to_datetime(
        df["Año"].astype(str) + "-" + df["Mes"].astype(str).str.zfill(2) + "-01",
        errors="coerce",
    ).dt.date

    if "Clave" in df.columns:
        df["Clave"] = df["Clave"].fillna("without_category")

    for col in ("Cuenta", "Centro", "Sección"):
        if col not in df.columns:
            df[col] = ""

    df["concatenado_2"] = (
        df["Cuenta"].astype(str) + "-" +
        df["Centro"].astype(str) + "-" +
        df["Sección"].astype(str)
    )

    return df


# ── Public API ───────────────────────────────────────────────────────────────

def fetch_balance(
    client_id: str = CLIENT_ID,
    tenant_id: str = TENANT_ID,
    pem_path:  str = PEM_PATH,
) -> pd.DataFrame:
    """
    Authenticate to SharePoint with the PEM certificate and return the combined
    BALANCE DataFrame, equivalent to the Power Query M pipeline output.

    Parameters
    ----------
    client_id : Azure AD App Registration client ID
    tenant_id : Azure AD tenant (GUID or domain, e.g. 'congroupiberiacsp.onmicrosoft.com')
    pem_path  : Path to the PEM file containing private key + certificate

    Returns
    -------
    pd.DataFrame with columns including: Empresa, Empresa Nombre, Fecha, Mes, Año,
    Nombre Mes, Saldo Mensual, fecha_reporte, Clave, concatenado_2, plus all
    original Excel columns.
    """
    token   = _get_token(client_id, tenant_id, pem_path)
    site_id = _get_site_id(token)
    files   = _list_balance_files(token, site_id)

    if not files:
        return pd.DataFrame()

    frames = []
    for f in files:
        try:
            raw = _read_excel(f["download_url"])
            frames.append(_transform(raw, f["name"]))
        except Exception as e:
            print(f"[sharepoint_balance] skipping {f['name']}: {e}")

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


# ── CLI entry point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    DB_PATH    = "mazda.duckdb"
    TABLE_NAME = "balance"

    print("Autenticando con SharePoint...")
    df = fetch_balance()

    if df.empty:
        print("No se encontraron archivos en BALANCE/Detalle.")
    else:
        print(f"  {len(df):,} filas · {len(df.columns)} columnas obtenidas")
        print(f"Cargando en {DB_PATH} → tabla '{TABLE_NAME}'...")

        con = duckdb.connect(DB_PATH)
        con.register("_balance_df", df)
        con.execute(f"CREATE OR REPLACE TABLE {TABLE_NAME} AS SELECT * FROM _balance_df")
        count = con.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]
        con.close()

        print(f"  Tabla '{TABLE_NAME}' creada con {count:,} filas.")
        print("Listo.")
