release: python manage.py migrate
web: gunicorn auth_service.wsgi:application --bind 0.0.0.0:$PORT
