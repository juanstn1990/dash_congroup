# Congroup Analytics v2.0

Dashboard interno de análisis de ventas y contabilidad para **Grupo Cars** (concesionario Mazda), migrado a **React + FastAPI** con mejoras visuales significativas.

---

## Arquitectura

```
├── backend/          # FastAPI + DuckDB
├── frontend/         # React 18 + Vite + TypeScript + Tailwind
├── nginx/            # Configuración de proxy inverso
├── docker-compose.yml
└── mazda.duckdb      # Base de datos (volumen)
```

---

## Stack

### Frontend
| Capa | Tecnología |
|---|---|
| Framework | React 18 + Vite |
| Lenguaje | TypeScript |
| Estilos | Tailwind CSS |
| UI | Componentes personalizados (estilo shadcn) |
| Gráficos | Recharts |
| Data fetching | TanStack Query |
| Routing | React Router DOM |
| Animaciones | Framer Motion |
| Íconos | Lucide React |
| Estado | Zustand |

### Backend
| Capa | Tecnología |
|---|---|
| Framework | FastAPI |
| Auth | JWT (PyJWT) |
| DB | DuckDB |
| Data | pandas, openpyxl |

---

## Desarrollo local

### Prerrequisitos
- Node.js 20+
- Python 3.11+
- `uv` o `pip`

### Backend

```bash
cd backend
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

URL: `http://localhost:8000/api/docs` (Swagger UI)

### Frontend

```bash
cd frontend
npm install
npm run dev
```

URL: `http://localhost:5173`

El proxy de Vite redirige `/api/*` al backend en `localhost:8000`.

---

## Producción (Docker)

```bash
docker compose up --build -d
```

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`

---

## Páginas

### 1. Resumen de Vendedores
- 5 KPIs con colores corporativos
- 4 gráficos interactivos (Recharts)
- Tabla detallada con exportación CSV
- Tabla pivot de ventas por tipo
- Filtros dinámicos por año y mes

### 2. Balance P&G
- 4 tabs: Resultado, vs Presupuesto, Presupuesto, vs Ejercicio Anterior
- Tablas contables con formato contable y colores condicionales
- Columnas sticky para Categoría/Concepto
- 4 gráficos contables (evolución, márgenes, áreas de negocio, cascada)
- Exportación a Excel
- KPIs contables en cards

---

## Credenciales

| Usuario | Contraseña |
|---|---|
| admin | admin |
| contabilidad_grupocars | contabilidad_grupocars |

---

## ETL (datos)

Los scripts de ingesta se mantienen en la raíz del proyecto:

```bash
python sharepoint_balance.py
python sharepoint_plantilla.py
python dataverse_categorias.py
```

Se requiere el certificado PEM (`CertificadoGrupoCars.pem`) para autenticación.

---

## Mejoras visuales respecto a v1 (Dash)

- ✅ UI moderna con Tailwind CSS
- ✅ Animaciones con Framer Motion
- ✅ Sidebar colapsable con transiciones suaves
- ✅ KPI cards con bordes de color y hover effects
- ✅ Gráficos Recharts con tooltips personalizados
- ✅ Tablas con sticky headers, sorting y colores condicionales
- ✅ Login con glassmorphism y animaciones
- ✅ Dark mode (base preparada)
- ✅ Skeleton loaders durante carga
- ✅ Exportación CSV/Excel
- ✅ Responsive design

---

> **Nota:** El proyecto anterior en Dash (`app.py`, `pages/balance.py`) se mantiene como referencia pero ya no se utiliza. La lógica de negocio fue migrada a `backend/app/services/`.
