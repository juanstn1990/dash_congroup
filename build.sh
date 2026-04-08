#!/bin/bash

echo "🐳 Construyendo imagen Docker: congroup-analytics"
echo "=================================================="

docker build -t congroup-analytics:latest .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Imagen construida exitosamente"
    echo ""
    echo "📦 Para ejecutar el contenedor:"
    echo "   ./run-docker.sh"
    echo ""
    echo "🔍 Para ver la imagen:"
    echo "   docker images | grep congroup"
else
    echo ""
    echo "❌ Error al construir la imagen"
    exit 1
fi
