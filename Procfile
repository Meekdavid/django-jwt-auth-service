release: python manage.py migrate
web: gunicorn auth_service.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 60 --log-level info
