# django_elastic_blog

Django REST API demo integrated with Elasticsearch (using elasticsearch-dsl).
Features: indexing, search (multi-match, nested), aggregations, scripting, bulk reindex.

## Run
1. Start Elasticsearch 
2. Create virtualenv and install requirements
3. python manage.py migrate
4. python manage.py runserver
5. python manage.py reindex  # optional to reindex all DB objects to ES

Article and Author Management API

Project Description

This project is a RESTful API designed for managing articles and authors. It allows users to efficiently create, update, delete, and search for articles and authors.
With Elasticsearch integration, it supports advanced search capabilities and filtering.

Roadmap

Administrator:
Full CRUD access to authors and articles
Ability to manage all resources

User:
Browse and search articles
Filter articles by tags, categories, and author names

API Endpoints
Authors Endpoints
Action	Method	URL	Description
Create Author	POST	/authors/create/	Create a new author
List Authors	GET	/authors/list/	List all authors. Supports filtering by name or specialization
Find Author by Article ID	GET	/authors/byArticle/<article_id>/	Find the author of a specific article
Retrieve Author Details	GET	/authors/str:pk
/	Get detailed information about a specific author
Update Author	PUT	/authors/str:pk
/	Update author information
Delete Author	DELETE	/authors/str:pk
/	Delete a specific author
Count Articles by Author	GET	/authors/count/	Get the number of articles per author

Example: Create Author

{
  "name": "Author Name",
  "specialization": "Author Specialization",
  "biography": "Biography of the author"
}

Articles Endpoints
Action	Method	URL	Description
Create Article	POST	/articles/create/	Create a new article
List Articles	GET	/articles/list/	List all articles. Supports filtering by title, tags, and categories
Search Articles	GET	/articles/search/	Advanced search with query parameters: keyword, tags, categories, author, start_date, end_date
Retrieve Article Details	GET	/articles/str:pk
/	Get detailed information about a specific article
Update Article	PUT	/articles/str:pk
/	Update a specific article
Delete Article	DELETE	/articles/str:pk
/	Delete a specific article
Calculate Common Tags	POST	/articles/str:article_id
/calculate-common-tags/	Calculate and update common tags for an article and return similar articles

Example: Create Article

{
  "title": "Article Title",
  "content": "Content of the article",
  "author": {
    "name": "Author Name",
    "email": "author@example.com"
  },
  "tags": ["tag1", "tag2"],
  "categories": ["category1", "category2"]
}
Description: Aggregates articles by tags and published date (monthly). Returns counts for each tag and month.

How to Use the API
Installation
bash
Copy code
git clone <repository-url>
cd <repository-directory>
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
Authentication
No authentication is required for creating or viewing articles. Write operations use the respective endpoints.