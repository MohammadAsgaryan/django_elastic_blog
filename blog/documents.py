from django.conf import settings
from elasticsearch_dsl import Document, Text, Keyword, Date, Nested, Integer, connections
from .models import Article


hosts = settings.ELASTICSEARCH_DSL['default']['hosts']
connections.create_connection(hosts=hosts)

class ArticleIndex(Document):
    title = Text()
    content = Text()
    category = Keyword()
    published_date = Date()
    tags = Nested(properties={
        'name': Text(),
        'value': Keyword()
    })
    views = Integer()

    class Index:
        name = 'articles'

    @classmethod
    def from_article(cls, article: Article):
        return cls(
            meta={'id': article.id},
            title=article.title,
            content=article.content,
            category=article.category,
            published_date=article.published_date,
            tags=article.tags,
            views=article.views
        )
