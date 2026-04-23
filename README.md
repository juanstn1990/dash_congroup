# Congroup Analytics

Dashboard interno de análisis de ventas y contabilidad para **Grupo Cars** (concesionario Mazda), construido con Dash + DuckDB y desplegado en Docker.

---

## Páginas

### 1. Resumen de Vendedores
Análisis operativo del equipo de ventas filtrado por año y mes.

**KPIs:**
- Con Placa · Subidos · Pendientes · Pedidos · Ventas

**Gráficos:**
- Top 10 vendedores por pedidos
- Ventas vs Pendientes (barras agrupadas)
- Media de BBs (BB1 / BB2 / BB3)
- Subidos vs Pendientes (barras apiladas)
- Distribución por tipo de venta (Top 10, barras apiladas)

**Tablas:**
- Resumen por vendedor: 14 columnas con BBs, descuentos, expedientes y financiaciones
- Pivot de ventas por tipo de venta con columna de vendedor sticky

---

### 2. Balance
Análisis contable P&G construido a partir de los archivos de balance de SharePoint y la plantilla de estructura contable.

**Tabla P&G:**
- Columnas por mes con sombreado alternado para diferenciarlos
- Columnas Categoría y Concepto fijas al hacer scroll horizontal
- Separador visual entre meses
- Jerarquía visual: filas hoja con sangría, filas de total en negrita
- Valores negativos en formato contable: `(1.234)`
- Porcentajes en verde/rojo según signo

**KPIs:**
- PyG Total · BN Total · Gastos Generales · Gastos Personal · Mejor Mes · Peor Mes

**Gráficos:**
- Evolución mensual del PyG vs BN Total
- Evolución de márgenes % (BB VN, BN VN, BN Total, PyG)
- BN por área de negocio (VN / VO / Posventa) por mes
- Cascada del resultado (waterfall: BN Total → Gastos → Res. I+A → Intereses → PyG)

---

## ETL — Carga de datos

Los scripts de ingesta se ejecutan manualmente y cargan datos en `mazda.duckdb`.

### SharePoint (autenticación por certificado PEM)

```bash
# Carga tabla `balance` — archivos Excel de BALANCE/Detalle
python sharepoint_balance.py

# Carga tabla `plantilla_resultado` — estructura contable (Hoja1 de Plantilla Resultado.xlsx)
python sharepoint_plantilla.py
```

### Dataverse / Dynamics 365

```bash
# Carga tabla `categorias` — entidad cgib_categorias
python dataverse_categorias.py
```

La autenticación usa el mismo certificado PEM (`CertificadoGrupoCars.pem`) con MSAL. `sharepoint_balance.py` expone `_get_token` con `scopes` opcional; los otros scripts lo importan directamente.

---

## Base de datos

Archivo único: `mazda.duckdb`. Tablas:

| Tabla | Origen | Descripción |
|---|---|---|
| `pedidosmazdas` | Parquet | Pedidos de vehículos Mazda |
| `stockvehiculosmazdas` | Parquet | Stock de vehículos |
| `vendedors` | Parquet | Catálogo de vendedores |
| `balance` | SharePoint | Saldos mensuales por empresa y cuenta |
| `plantilla_resultado` | SharePoint | Estructura contable P&G (N, Concepto, Categoria, GrupoPadre, Porcentaje) |
| `categorias` | Dataverse | Categorías contables (cgib_categorias) |

---

## Despliegue

```bash
# Construir y levantar
docker compose up --build -d

# Ver logs
docker logs -f congroup-analytics-dashboard

# Detener
docker compose down
```

URL: `http://localhost:8052`  
Credenciales: `admin` / `admin`

El archivo `mazda.duckdb` se monta como volumen — los datos persisten entre reinicios del contenedor.

---

## Desarrollo local

```bash
pip install -r requirements.txt
python app.py
```

---

## Stack

| Capa | Tecnología |
|---|---|
| Dashboard | Dash (Plotly) + Dash Bootstrap Components |
| Backend | Flask + Flask-Login |
| Base de datos | DuckDB |
| ETL SharePoint | MSAL + Microsoft Graph API + openpyxl |
| ETL Dataverse | MSAL + Dataverse Web API v9.2 |
| Contenedor | Docker + Docker Compose |
| Python | 3.11 |

---

## Estructura

```
streamlit_congroup/
├── app.py                      # App principal: rutas, layout, callbacks
├── queries.py                  # Consultas SQL para pedidos Mazda
├── sharepoint_balance.py       # ETL: BALANCE/Detalle → tabla balance
├── sharepoint_plantilla.py     # ETL: Plantilla Resultado.xlsx → tabla plantilla_resultado
├── dataverse_categorias.py     # ETL: cgib_categorias → tabla categorias
├── pages/
│   └── balance.py              # Página Balance: tabla P&G + gráficos contables
├── assets/
│   └── Logo_congroup-web2.png
├── mazda.duckdb                # Base de datos (gitignore recomendado)
├── CertificadoGrupoCars.pem    # Certificado de autenticación (NO versionar)
├── Dockerfile
└── docker-compose.yml
```

> **Seguridad:** el archivo `.pem` y `mazda.duckdb` no deben subirse al repositorio.
