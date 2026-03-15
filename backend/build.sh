#!/bin/bash
set -e

echo "🔧 Instalando dependencias..."
pip install -r requirements.txt

echo "🔄 Aplicando migraciones..."
python manage.py migrate --no-input

echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --no-input

echo "👤 Creando superusuario..."
python manage.py shell << 'PYEOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@gymdado.com',
        password='dieguito19'
    )
    print('Superusuario creado exitosamente')
else:
    print('Superusuario ya existe')
PYEOF

echo "✅ Build completado"