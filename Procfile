release: python manage.py migrate --noinput
web: bash -c "gunicorn auth_service.wsgi:application --bind 0.0.0.0:\${PORT:-8000} --log-file -"
