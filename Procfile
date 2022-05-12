release: python manage.py migrate
web: gunicorn SecureCity.wsgi:application --log-file - --log-level debug
python manage.py collectstatic --noinput
manage.py migrate
