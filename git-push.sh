#!/bin/bash

echo "🔄 Publicando cambios en GitHub"
echo "================================"
echo ""

# Verificar si hay cambios
if [[ -z $(git status -s) ]]; then
    echo "⚠️  No hay cambios para publicar"
    exit 0
fi

# Mostrar cambios
echo "📝 Cambios detectados:"
git status -s
echo ""

# Pedir mensaje de commit
read -p "📋 Mensaje del commit: " commit_message

if [ -z "$commit_message" ]; then
    echo "❌ Mensaje de commit vacío. Abortando."
    exit 1
fi

# Agregar todos los cambios
echo ""
echo "➕ Agregando archivos..."
git add -A

# Crear commit
echo "💾 Creando commit..."
git commit -m "$commit_message"

# Push a GitHub
echo "🚀 Publicando en GitHub..."
git push origin master

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Cambios publicados exitosamente"
    echo "🔗 https://github.com/juanstn1990/dash_congroup"
else
    echo ""
    echo "❌ Error al publicar cambios"
    exit 1
fi
