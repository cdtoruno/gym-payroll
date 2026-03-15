#!/bin/bash
set -e

echo "🔧 Instalando dependencias..."
pip install -r requirements.txt

echo "🔄 Aplicando migraciones..."
python manage.py migrate --no-input

echo "✅ Build completado"

echo "👤 Creando superusuario..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@gym.com', 'Dieguito19')
    print('Superusuario creado')
else:
    print('Superusuario ya existe')
"