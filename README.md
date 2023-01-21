# envri-kbs

```
python3 -m spacy download en_core_web_md
```
```
manage.py migrate
manage.py  makemigrations
manage.py  runserver 0.0.0.0:8000
```

## Environment variables

- ACCESS_TOKEN_Github=<A_GITHUB_TOKEN>
- ACCESS_TOKEN_Gitlab==<A_GITLAB_TOKEN>
- ELASTICSEARCH_PASSWORD=<ES_PASSWORD>
- ELASTICSEARCH_URL=https://HOST:PORT/BASE_PATH/
- ELASTICSEARCH_USERNAME=<ES_USERNAME>
- GITHUB_QUERY_URL=https://api.github.com/search/code?l=Jupyter+Notebook&q=ipynb+in:path+extension:ipynb
- KMS_ADMIN_USERNAME=<ADMIN_USERNAME>
- KMS_ADMIN_PASSWORD=<ADMIN_PASSWORD>