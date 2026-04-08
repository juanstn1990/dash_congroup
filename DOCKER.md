# 🐳 Guía Docker - Congroup Analytics

## 📦 Archivos Docker

```
streamlit_congroup/
├── Dockerfile              # Configuración de la imagen Docker
├── docker-compose.yml      # Orquestación (opcional)
├── .dockerignore          # Archivos excluidos de la imagen
├── build.sh               # Script para construir la imagen
├── run-docker.sh          # Script para ejecutar el contenedor
└── stop-docker.sh         # Script para detener el contenedor
```

## 🚀 Inicio Rápido

### 1. Construir la Imagen

```bash
./build.sh
```

Este comando:
- Construye la imagen Docker llamada `congroup-analytics:latest`
- Instala todas las dependencias Python
- Configura el entorno de ejecución
- Crea un usuario no-root para seguridad

**Tiempo aproximado**: 2-5 minutos en la primera construcción

### 2. Ejecutar el Contenedor

```bash
./run-docker.sh
```

Este comando:
- Detiene cualquier contenedor anterior
- Inicia un nuevo contenedor llamado `congroup-analytics-dashboard`
- Mapea el puerto 8052 del contenedor al puerto 8052 del host
- Monta la base de datos como volumen para persistencia
- Configura reinicio automático

**Acceso**: http://localhost:8052

### 3. Detener el Contenedor

```bash
./stop-docker.sh
```

## 📋 Comandos Útiles

### Ver Estado

```bash
# Ver si el contenedor está corriendo
docker ps | grep congroup

# Ver todos los contenedores (incluyendo detenidos)
docker ps -a | grep congroup

# Ver información detallada
docker inspect congroup-analytics-dashboard
```

### Ver Logs

```bash
# Ver logs en tiempo real
docker logs -f congroup-analytics-dashboard

# Ver últimas 100 líneas
docker logs --tail 100 congroup-analytics-dashboard

# Ver logs con timestamp
docker logs -t congroup-analytics-dashboard
```

### Gestión del Contenedor

```bash
# Reiniciar el contenedor
docker restart congroup-analytics-dashboard

# Detener el contenedor
docker stop congroup-analytics-dashboard

# Iniciar contenedor detenido
docker start congroup-analytics-dashboard

# Eliminar contenedor
docker rm congroup-analytics-dashboard

# Eliminar contenedor forzadamente
docker rm -f congroup-analytics-dashboard
```

### Gestión de Imágenes

```bash
# Ver imágenes disponibles
docker images | grep congroup

# Eliminar imagen
docker rmi congroup-analytics:latest

# Eliminar imágenes sin usar
docker image prune

# Ver espacio usado
docker system df
```

### Debugging

```bash
# Entrar al contenedor en ejecución
docker exec -it congroup-analytics-dashboard /bin/bash

# Ejecutar comando dentro del contenedor
docker exec congroup-analytics-dashboard ls -la /app

# Ver recursos usados
docker stats congroup-analytics-dashboard

# Ver procesos dentro del contenedor
docker top congroup-analytics-dashboard
```

## 🔧 Configuración Avanzada

### Variables de Entorno

Editar `docker-compose.yml` o usar `-e` en `docker run`:

```bash
docker run -d \
  --name congroup-analytics-dashboard \
  -p 8052:8052 \
  -e PORT=8052 \
  -e PYTHONUNBUFFERED=1 \
  congroup-analytics:latest
```

### Cambiar Puerto

```bash
# Mapear a puerto diferente (ej: 9000)
docker run -d \
  --name congroup-analytics-dashboard \
  -p 9000:8052 \
  congroup-analytics:latest

# Acceso: http://localhost:9000
```

### Volúmenes Adicionales

```bash
# Montar múltiples archivos
docker run -d \
  --name congroup-analytics-dashboard \
  -p 8052:8052 \
  -v "$(pwd)/mazda.duckdb:/app/mazda.duckdb" \
  -v "$(pwd)/pedidosmazdas.parquet:/app/pedidosmazdas.parquet" \
  congroup-analytics:latest
```

### Límites de Recursos

```bash
# Limitar CPU y Memoria
docker run -d \
  --name congroup-analytics-dashboard \
  -p 8052:8052 \
  --cpus="1.5" \
  --memory="1g" \
  congroup-analytics:latest
```

## 🔄 Actualización

### Actualizar Código

```bash
# 1. Detener contenedor
./stop-docker.sh

# 2. Reconstruir imagen
./build.sh

# 3. Ejecutar nuevo contenedor
./run-docker.sh
```

### Actualizar Solo Datos

```bash
# 1. Detener contenedor
docker stop congroup-analytics-dashboard

# 2. Actualizar archivos .parquet y .duckdb

# 3. Iniciar contenedor
docker start congroup-analytics-dashboard
```

## 🐛 Troubleshooting

### El contenedor no inicia

```bash
# Ver logs de error
docker logs congroup-analytics-dashboard

# Verificar que la imagen existe
docker images | grep congroup

# Verificar puerto disponible
netstat -tulpn | grep 8052
```

### Puerto ya en uso

```bash
# Encontrar proceso usando el puerto
lsof -i :8052

# Usar puerto diferente
docker run -d --name congroup-analytics-dashboard -p 9000:8052 congroup-analytics:latest
```

### Error de permisos con la base de datos

```bash
# Dar permisos correctos
chmod 644 mazda.duckdb

# O ejecutar como root (no recomendado)
docker run -d --name congroup-analytics-dashboard -u root -p 8052:8052 congroup-analytics:latest
```

### Contenedor se detiene inmediatamente

```bash
# Ver logs completos
docker logs congroup-analytics-dashboard

# Ejecutar en modo interactivo para debug
docker run -it --rm congroup-analytics:latest /bin/bash
```

### Memoria insuficiente

```bash
# Ver uso de recursos
docker stats

# Aumentar límite de memoria
docker run -d --name congroup-analytics-dashboard --memory="2g" -p 8052:8052 congroup-analytics:latest
```

## 📊 Healthcheck

El contenedor incluye un healthcheck automático que verifica cada 30 segundos si la aplicación responde.

```bash
# Ver estado de salud
docker inspect --format='{{.State.Health.Status}}' congroup-analytics-dashboard

# Ver historial de healthchecks
docker inspect --format='{{json .State.Health}}' congroup-analytics-dashboard | jq
```

## 🔐 Seguridad

### Usuario No-Root

La imagen ejecuta la aplicación como usuario `appuser` (UID 1000) para mayor seguridad.

### Cambiar Credenciales

Editar `app.py` línea 32:

```python
VALID_USERS = {'admin': 'admin'}  # Cambiar esto
```

Reconstruir imagen después de cambios.

## 📦 Exportar/Importar Imagen

### Exportar imagen

```bash
# Guardar imagen en archivo
docker save congroup-analytics:latest | gzip > congroup-analytics.tar.gz

# Ver tamaño
ls -lh congroup-analytics.tar.gz
```

### Importar imagen

```bash
# Cargar imagen desde archivo
docker load < congroup-analytics.tar.gz

# Verificar
docker images | grep congroup
```

## 🌐 Deployment en Servidor

### Usando Docker

```bash
# 1. Copiar archivos al servidor
scp -r . usuario@servidor:/opt/congroup-analytics/

# 2. SSH al servidor
ssh usuario@servidor

# 3. Construir y ejecutar
cd /opt/congroup-analytics
./build.sh
./run-docker.sh
```

### Usar imagen pre-construida

```bash
# 1. Exportar en local
docker save congroup-analytics:latest | gzip > congroup-analytics.tar.gz

# 2. Copiar al servidor
scp congroup-analytics.tar.gz usuario@servidor:/tmp/

# 3. Cargar en servidor
ssh usuario@servidor
docker load < /tmp/congroup-analytics.tar.gz
./run-docker.sh
```

---

**Versión Docker**: 2.0  
**Imagen Base**: python:3.11-slim  
**Puerto**: 8052  
**Usuario**: appuser (UID 1000)
