# Congroup Analytics - Dashboard de Ventas Mazda

Dashboard interactivo para análisis de ventas y rendimiento de vendedores en Grupo Cars Mazda.

## 📊 Características

- **Autenticación segura** con Flask-Login
- **5 KPIs principales**: Con Placa, Subidos, Pendientes, Pedidos, Ventas
- **4 Gráficos interactivos**: Top vendedores, distribución, BBs, expedientes
- **Tabla de resumen detallada** con 14 columnas y totales
- **Análisis por tipo de venta** con tabla pivotada y gráfico de distribución
- **Filtros dinámicos** por año y mes
- **Login modernizado** con diseño azul elegante

## 🚀 Inicio Rápido con Docker

### Prerrequisitos

- Docker instalado

### Método 1: Scripts automatizados (Recomendado)

```bash
# 1. Construir la imagen
./build.sh

# 2. Ejecutar el contenedor
./run-docker.sh

# 3. Ver logs
docker logs -f congroup-analytics-dashboard

# 4. Detener
./stop-docker.sh
```

### Método 2: Docker Compose (si está disponible)

```bash
# Construir y ejecutar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

### Método 3: Comandos Docker manuales

```bash
# Construir imagen
docker build -t congroup-analytics:latest .

# Ejecutar contenedor
docker run -d \
  --name congroup-analytics-dashboard \
  -p 8052:8052 \
  -v "$(pwd)/mazda.duckdb:/app/mazda.duckdb" \
  --restart unless-stopped \
  congroup-analytics:latest

# Ver logs
docker logs -f congroup-analytics-dashboard

# Detener
docker stop congroup-analytics-dashboard
```

### Acceder al Dashboard

Abre tu navegador en:
```
http://localhost:8052
```

**Credenciales:**
- Usuario: `admin`
- Contraseña: `admin`

## 🐳 Comandos Docker Útiles

```bash
# Ver estado del contenedor
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f congroup-analytics

# Reiniciar el servicio
docker-compose restart

# Reconstruir después de cambios
docker-compose up -d --build

# Entrar al contenedor
docker-compose exec congroup-analytics /bin/bash

# Ver uso de recursos
docker stats congroup-analytics-dashboard
```

## 📦 Estructura del Proyecto

```
streamlit_congroup/
├── app.py                          # Aplicación principal Dash
├── queries.py                      # Consultas SQL y funciones de datos
├── requirements.txt                # Dependencias Python
├── Dockerfile                      # Configuración Docker
├── docker-compose.yml              # Orquestación Docker
├── .dockerignore                   # Archivos excluidos de la imagen
├── mazda.duckdb                    # Base de datos DuckDB
├── *.parquet                       # Archivos de datos
├── assets/                         # Recursos estáticos
│   └── Logo_congroup-web2.png     # Logo corporativo
└── pages/                          # Módulo de páginas
    └── __init__.py
```

## 🔧 Desarrollo Local (sin Docker)

### Prerrequisitos

- Python 3.11+
- pip

### Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python app.py
```

La aplicación estará disponible en `http://localhost:8052`

## 📊 Componentes del Dashboard

### 1. Login
- Diseño azul moderno con degradados
- Efecto glassmorphism
- Validación de credenciales

### 2. KPIs
- **Con Placa**: Registros con fecha de matriculación
- **Subidos**: Registros con expediente
- **Pendientes**: Registros sin expediente
- **Pedidos**: Total de pedidos (por fecha de pedido)
- **Ventas**: Total de ventas (por fecha de aviso)

### 3. Gráficos
- **Top 10 Vendedores por Pedidos**: Barras horizontales
- **Ventas vs Pendientes**: Barras agrupadas
- **Media de BBs**: Gráfico de líneas
- **Subidos vs Pendientes**: Barras apiladas

### 4. Tabla de Resumen
- 14 columnas con métricas detalladas
- Fila de totales
- Ordenamiento y filtrado nativos
- Scroll vertical con header sticky

### 5. Análisis por Tipo de Venta
- **Tabla pivotada**: Tipos de venta en columnas
- **Columna sticky**: Vendedor siempre visible
- **Fila de totales**: Con estilo especial
- **Gráfico de distribución**: Top 10 vendedores

### 6. Filtros
- Año (predeterminado: año actual)
- Mes (predeterminado: mes actual)
- Aplica a todos los gráficos y tablas

## 🔐 Seguridad

- Autenticación mediante Flask-Login
- Sesiones seguras en servidor
- Usuario/contraseña configurables en `app.py` (línea 32)

**⚠️ Importante**: Cambiar las credenciales por defecto en producción.

## 🗄️ Base de Datos

El dashboard utiliza **DuckDB** con los siguientes archivos:

- `mazda.duckdb`: Base de datos principal
- `pedidosmazdas.parquet`: Tabla de pedidos
- `stockvehiculosmazdas.parquet`: Tabla de stock
- `vendedors.parquet`: Tabla de vendedores
- `resumen_vendedores.parquet`: Tabla de resumen

## 📈 Métricas y Cálculos

### Definiciones

- **Pedidos**: Filtrado por `cgib_fechainicialdelpedido`
- **Ventas**: Filtrado por `FechaSimulada` (mes de aviso)
- **Subidos**: Registros con `nro_expediente IS NOT NULL`
- **Pendientes**: Registros con `nro_expediente IS NULL`
- **Con Placa**: Registros con `fecha_matriculacion_stock IS NOT NULL`
- **Operaciones Financiadas**: Registros con `importe_financiacion > 0`

### Tipos de Venta

37 tipos diferentes incluyendo:
- Cliente Particular
- Fidelización/Sobretasación
- Flota Dealer
- Empresas y Autónomos
- Mazda Renting
- Mazda Exclusive Days
- Y más...

## 🎨 Tecnologías

- **Backend**: Python 3.11, Flask
- **Dashboard**: Dash (Plotly)
- **Base de datos**: DuckDB
- **Autenticación**: Flask-Login
- **UI Components**: Dash Bootstrap Components
- **Gráficos**: Plotly
- **Containerización**: Docker

## 📝 Variables de Entorno

Puedes configurar las siguientes variables en `docker-compose.yml`:

```yaml
environment:
  - PORT=8052                    # Puerto de la aplicación
  - PYTHONUNBUFFERED=1           # Logs en tiempo real
```

## 🔄 Actualización de Datos

Para actualizar los datos de la base de datos:

1. Detén el contenedor: `docker-compose down`
2. Reemplaza `mazda.duckdb` y los archivos `.parquet`
3. Inicia el contenedor: `docker-compose up -d`

## 🐛 Troubleshooting

### El contenedor no inicia

```bash
# Ver logs detallados
docker-compose logs congroup-analytics

# Verificar que el puerto 8052 esté libre
netstat -an | grep 8052
```

### Error de permisos con la base de datos

```bash
# Asegurar permisos correctos
chmod 644 mazda.duckdb
```

### La aplicación es lenta

```bash
# Verificar recursos del contenedor
docker stats congroup-analytics-dashboard

# Ajustar recursos en docker-compose.yml si es necesario
```

## 📄 Licencia

Propiedad de Grupo Cars Mazda - Uso Interno

## 👥 Soporte

Para soporte técnico, contactar al equipo de IT de Congroup.

---

**Versión**: 2.0  
**Última actualización**: Abril 2026  
**Docker Ready**: ✅
