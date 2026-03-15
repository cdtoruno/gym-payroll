#!/bin/bash
set -e

echo "🔧 Instalando dependencias..."
pip install -r requirements.txt

echo "📁 Creando carpeta staticfiles..."
mkdir -p staticfiles

echo "🔄 Generando migraciones pendientes..."
python manage.py makemigrations --no-input

echo "🔄 Aplicando migraciones..."
python manage.py migrate --no-input

echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --no-input

echo "✅ Build completado"