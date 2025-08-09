web: gunicorn bazarche_project.wsgi --log-file -
release: python manage.py migrate && python manage.py collectstatic --noinput && python manage.py seed_production_data 