#!/bin/bash

echo "🚀 Iniciando Congroup Analytics Dashboard"
echo "=========================================="

# Detener contenedor existente si está corriendo
docker stop congroup-analytics-dashboard 2>/dev/null
docker rm congroup-analytics-dashboard 2>/dev/null

# Ejecutar contenedor
docker run -d \
  --name congroup-analytics-dashboard \
  -p 8052:8052 \
  -v "$(pwd)/mazda.duckdb:/app/mazda.duckdb" \
  --restart unless-stopped \
  congroup-analytics:latest

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Contenedor iniciado exitosamente"
    echo ""
    echo "🌐 Dashboard disponible en:"
    echo "   http://localhost:8052"
    echo ""
    echo "👤 Credenciales:"
    echo "   Usuario: admin"
    echo "   Contraseña: admin"
    echo ""
    echo "📋 Comandos útiles:"
    echo "   Ver logs:      docker logs -f congroup-analytics-dashboard"
    echo "   Detener:       docker stop congroup-analytics-dashboard"
    echo "   Estado:        docker ps | grep congroup"
else
    echo ""
    echo "❌ Error al iniciar el contenedor"
    exit 1
fi
