# django_elastic_blog

Django REST API demo integrated with Elasticsearch (using elasticsearch-dsl).
Features: indexing, search (multi-match, nested), aggregations, scripting, bulk reindex.

## Run
1. Start Elasticsearch 
2. Create virtualenv and install requirements
3. python manage.py migrate
4. python manage.py runserver
5. python manage.py reindex  # optional to reindex all DB objects to ES
