# django_elastic_blog

Django REST API demo integrated with Elasticsearch (using elasticsearch-dsl).
Features: indexing, search (multi-match, nested), aggregations, scripting, bulk reindex.

## Run
1. Start Elasticsearch 
2. Create virtualenv and install requirements
3. python manage.py migrate
4. python manage.py runserver
5. python manage.py reindex  # optional to reindex all DB objects to ES


 Article Management API

Project Description
This project is a RESTful API designed for managing articles, providing a seamless and efficient way for users to create, update, delete, and search for articles. The API facilitates essential functionalities, allowing users to manage articles and perform advanced queries using Elasticsearch. Nested tags with name and description fields are supported.


 Roadmap
- As an administrator, you can add, update, or delete articles and have full access to CRUD operations.  
- As a user, you can browse and search articles based on various filters like tags, categories, and published date.

API Endpoints

Articles Endpoints

Create Article
- **Method:** POST  
- **URL:** /articles/create/  
- **Request Body:**
```json
{
  "title": "Article Title",
  "content": "Content of the article",
  "category": "Category Name",
  "tags": [
    {"name": "tag1", "description": "Description 1"},
    {"name": "tag2", "description": "Description 2"}
  ]
}
List Articles
Method: GET
URL: /articles/list/

Description: Retrieves a list of all articles. You can filter by title, tags, and categories using query parameters.

Search Articles
Method: GET
URL: /articles/search/?q=<keyword>

Description: Performs an advanced search on articles based on the specified keyword. Returns a filtered list of articles with nested tags.

Retrieve Article Details
Method: GET
URL: /articles/int:pk/

Description: Retrieves detailed information about a specific article by its ID.

Update Article
Method: PUT
URL: /articles/int:pk/

Description: Updates the information of a specific article by its ID. Requires the same fields as create.

Delete Article
Method: DELETE
URL: /articles/int:pk/

Description: Deletes a specific article by its ID.

Bulk Create Articles
Method: POST
URL: /articles/bulk_create/

Request Body: Same structure as create article, but as a list under articles.

Bulk Update Articles
Method: POST
URL: /articles/bulk_update/

Request Body: Same structure as bulk create, each article must include its id.

Increment Article Views
Method: POST
URL: /articles/int:pk/increase-views/

Request Body:

json
Copy code
{
  "amount": 1
}
Article Aggregation
Method: GET
URL: /articles/aggregation/

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