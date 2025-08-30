release: python manage.py migrate --noinput
web: gunicorn auth_service.wsgi:application --bind 0.0.0.0:$PORT --log-file -
