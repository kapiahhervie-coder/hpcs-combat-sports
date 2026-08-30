release: python manage.py migrate --noinput && python manage.py collectstatic --noinput
web: gunicorn hpcs_config.wsgi --log-file -
