
python manage.py makemigrations
python manage.py migrate

# python -m notebooksearch.notebook_indexing

#gunicorn --bind :7777 --workers 4 search_engine_app.wsgi:application

python manage.py runserver 0.0.0.0:8000