release: python manage.py migrate --noinput
web: gunicorn auth_service.wsgi --log-file -
