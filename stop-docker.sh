#!/bin/bash

echo "🛑 Deteniendo Congroup Analytics Dashboard"
echo "==========================================="

docker stop congroup-analytics-dashboard

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Contenedor detenido"
    echo ""
    echo "📋 Para eliminar completamente:"
    echo "   docker rm congroup-analytics-dashboard"
    echo ""
    echo "📋 Para volver a iniciar:"
    echo "   ./run-docker.sh"
else
    echo ""
    echo "⚠️  El contenedor no estaba corriendo"
fi
