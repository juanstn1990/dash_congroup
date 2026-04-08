# 🚀 Guía de Despliegue - Congroup Analytics

**Proyecto dockerizado y listo para producción**

## 📦 Contenido del Proyecto

### Archivos Principales

```
congroup-analytics/
├── app.py (30KB)                    # Aplicación Dash con Flask-Login
├── queries.py (27KB)                # Consultas SQL a DuckDB
├── mazda.duckdb (11MB)              # Base de datos principal
├── requirements.txt                 # Dependencias Python
└── README.md                        # Documentación principal
```

### Datos

```
├── pedidosmazdas.parquet (1.3MB)           # Pedidos de vehículos
├── stockvehiculosmazdas.parquet (214KB)    # Inventario
├── vendedors.parquet (29KB)                # Vendedores
└── resumen_vendedores.parquet (15KB)       # Resumen precalculado
```

### Docker

```
├── Dockerfile                       # Configuración de imagen
├── docker-compose.yml               # Orquestación (opcional)
├── .dockerignore                    # Exclusiones
├── build.sh                         # Script de construcción
├── run-docker.sh                    # Script de ejecución
├── stop-docker.sh                   # Script de parada
└── DOCKER.md                        # Guía completa Docker
```

### Assets

```
└── assets/
    └── Logo_congroup-web2.png       # Logo corporativo
```

## 🎯 Métodos de Despliegue

### 1. Desarrollo Local (Sin Docker)

**Uso**: Desarrollo y testing

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python app.py

# Acceso: http://localhost:8052
```

**Ventajas**: 
- Rápido para desarrollo
- Fácil debugging
- Sin overhead de Docker

**Desventajas**:
- Depende del entorno Python local
- No reproducible entre máquinas

---

### 2. Docker Local

**Uso**: Testing pre-producción

```bash
# Construcción
./build.sh

# Ejecución
./run-docker.sh

# Acceso: http://localhost:8052
```

**Ventajas**:
- Entorno aislado
- Reproducible
- Simula producción

**Desventajas**:
- Requiere Docker instalado
- Construcción inicial lenta (2-5 min)

---

### 3. Docker Compose

**Uso**: Producción local o servidor único

```bash
# Todo en uno
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

**Ventajas**:
- Configuración declarativa
- Fácil escalado
- Network automático

**Desventajas**:
- Requiere Docker Compose
- Más complejo para casos simples

---

### 4. Servidor de Producción

**Uso**: Deployment en servidor Linux

#### Opción A: Transferir y construir

```bash
# 1. En local - empaquetar
tar -czf congroup-analytics.tar.gz .

# 2. Copiar al servidor
scp congroup-analytics.tar.gz user@server:/opt/

# 3. En servidor - descomprimir
ssh user@server
cd /opt
tar -xzf congroup-analytics.tar.gz

# 4. Construir y ejecutar
./build.sh
./run-docker.sh
```

#### Opción B: Transferir imagen

```bash
# 1. En local - exportar imagen
./build.sh
docker save congroup-analytics:latest | gzip > image.tar.gz

# 2. Copiar al servidor
scp image.tar.gz user@server:/tmp/

# 3. En servidor - cargar imagen
ssh user@server
docker load < /tmp/image.tar.gz
./run-docker.sh
```

**Ventajas**:
- Permanente
- Configuración de reinicio automático
- Acceso remoto

**Desventajas**:
- Requiere configuración de servidor
- Necesita gestionar actualizaciones

---

### 5. Cloud (AWS, Azure, GCP)

**Uso**: Producción escalable

#### Container Registry

```bash
# 1. Tag para registry
docker tag congroup-analytics:latest registry.example.com/congroup-analytics:latest

# 2. Push
docker push registry.example.com/congroup-analytics:latest

# 3. Deploy en cloud
# (específico de cada proveedor)
```

#### AWS ECS/Fargate

```bash
# 1. Crear repositorio ECR
aws ecr create-repository --repository-name congroup-analytics

# 2. Login
aws ecr get-login-password | docker login --username AWS --password-stdin <registry>

# 3. Tag y push
docker tag congroup-analytics:latest <ecr-url>/congroup-analytics:latest
docker push <ecr-url>/congroup-analytics:latest

# 4. Crear tarea ECS
# (usar AWS Console o CloudFormation)
```

**Ventajas**:
- Alta disponibilidad
- Escalabilidad automática
- Backups automáticos

**Desventajas**:
- Costo mensual
- Complejidad de configuración
- Requiere conocimientos cloud

---

## 🔐 Configuración de Producción

### 1. Cambiar Credenciales

**Archivo**: `app.py` línea 32

```python
# Antes (desarrollo)
VALID_USERS = {'admin': 'admin'}

# Después (producción)
VALID_USERS = {
    'usuario1': 'contraseña_segura_hash',
    'usuario2': 'otra_contraseña_hash'
}
```

**⚠️ Importante**: Usar hashing de contraseñas (bcrypt, argon2)

### 2. Variables de Entorno

Crear archivo `.env` (no versionar):

```bash
# .env
FLASK_SECRET_KEY=your-secret-key-here
ADMIN_PASSWORD=secure-password
PORT=8052
DEBUG=False
```

### 3. SSL/HTTPS

#### Opción A: Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl;
    server_name analytics.congroup.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8052;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Opción B: Traefik

```yaml
# docker-compose.yml
services:
  congroup-analytics:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.analytics.rule=Host(`analytics.congroup.com`)"
      - "traefik.http.routers.analytics.tls=true"
```

### 4. Backup de Datos

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/congroup-analytics"

# Crear directorio
mkdir -p $BACKUP_DIR

# Backup base de datos
cp mazda.duckdb $BACKUP_DIR/mazda_$DATE.duckdb

# Backup parquets
tar -czf $BACKUP_DIR/data_$DATE.tar.gz *.parquet

# Mantener solo últimos 30 días
find $BACKUP_DIR -mtime +30 -delete

echo "✅ Backup completado: $DATE"
```

Configurar cron:

```bash
# Ejecutar diariamente a las 2 AM
0 2 * * * /opt/congroup-analytics/backup.sh
```

---

## 📊 Monitoreo

### 1. Healthcheck

Verificar que la app responde:

```bash
# Manual
curl http://localhost:8052

# Automático (cada 5 min)
*/5 * * * * curl -f http://localhost:8052 || systemctl restart docker-congroup
```

### 2. Logs

```bash
# Ver logs del contenedor
docker logs -f congroup-analytics-dashboard

# Rotar logs
docker run -d \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  congroup-analytics:latest
```

### 3. Recursos

```bash
# Ver uso en tiempo real
docker stats congroup-analytics-dashboard

# Limitar recursos
docker update --memory="1g" --cpus="1" congroup-analytics-dashboard
```

---

## 🔄 Actualización

### Actualizar Código

```bash
# 1. Backup
./backup.sh

# 2. Detener
./stop-docker.sh

# 3. Pull cambios (si usa git)
git pull

# 4. Reconstruir
./build.sh

# 5. Reiniciar
./run-docker.sh

# 6. Verificar
docker logs -f congroup-analytics-dashboard
```

### Actualizar Solo Datos

```bash
# 1. Detener
docker stop congroup-analytics-dashboard

# 2. Reemplazar archivos
cp nuevo_mazda.duckdb mazda.duckdb
cp nuevos/*.parquet .

# 3. Iniciar
docker start congroup-analytics-dashboard
```

---

## 🐛 Troubleshooting Producción

### App no accesible

```bash
# 1. Verificar contenedor
docker ps | grep congroup

# 2. Ver logs
docker logs congroup-analytics-dashboard

# 3. Verificar puerto
netstat -tulpn | grep 8052

# 4. Verificar firewall
sudo ufw status
sudo ufw allow 8052
```

### Performance lento

```bash
# 1. Ver recursos
docker stats

# 2. Aumentar límites
docker update --memory="2g" --cpus="2" congroup-analytics-dashboard

# 3. Revisar base de datos
# (optimizar queries en queries.py)
```

### Errores de base de datos

```bash
# 1. Verificar integridad
python -c "import duckdb; duckdb.connect('mazda.duckdb').execute('PRAGMA integrity_check')"

# 2. Restaurar backup
cp /backups/mazda_YYYYMMDD.duckdb mazda.duckdb

# 3. Reiniciar
docker restart congroup-analytics-dashboard
```

---

## 📋 Checklist Pre-Producción

- [ ] Credenciales cambiadas
- [ ] SSL configurado
- [ ] Backups automáticos
- [ ] Monitoreo configurado
- [ ] Logs rotando
- [ ] Firewall configurado
- [ ] DNS apuntando
- [ ] Recursos limitados
- [ ] Healthcheck funcionando
- [ ] Documentación actualizada

---

## 🌐 URLs y Accesos

### Desarrollo
- URL: http://localhost:8052
- Usuario: admin
- Contraseña: admin

### Producción (ejemplo)
- URL: https://analytics.congroup.com
- Usuario: configurar en producción
- Contraseña: configurar en producción

---

**Versión**: 2.0  
**Última actualización**: Abril 2026  
**Estado**: Listo para producción ✅
