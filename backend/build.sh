#!/bin/bash
set -e

echo "🔧 Instalando dependencias..."
pip install -r requirements.txt

echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --no-input

echo "🔄 Aplicando migraciones..."
python manage.py migrate

echo "✅ Build completado"