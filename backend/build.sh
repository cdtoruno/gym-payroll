#!/bin/bash
set -e

echo "🔧 Instalando dependencias..."
pip install -r requirements.txt

echo "🔄 Aplicando migraciones..."
python manage.py migrate --no-input

echo "✅ Build completado"