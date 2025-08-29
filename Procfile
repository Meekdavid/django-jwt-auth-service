release: python manage.py migrate --noinput
web: python manage.py collectstatic --noinput && gunicorn auth_service.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 60 --log-level info
