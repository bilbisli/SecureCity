release: python manage.py migrate
web: gunicorn SecureCity.SecureCity.wsgi:application --log-file - --log-level debug
