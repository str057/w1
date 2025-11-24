cat > entrypoint.sh << 'EOF'
#!/bin/bash

# Ожидание доступности базы данных
echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "Database started"

# Применение миграций
echo "Applying migrations..."
python manage.py migrate --noinput

# Создание суперпользователя (если нужно)
if [ "$CREATE_SUPERUSER" = "true" ]; then
  echo "Creating superuser..."
  python manage.py createsuperuser --noinput || true
fi

# Запуск сервера
echo "Starting server..."
exec gunicorn --bind 0.0.0.0:8000 your_project.wsgi:application
EOF