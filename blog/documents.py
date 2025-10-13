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
    
    tags = Nested(
        properties={
            'name': Text(),
            'description': Text()
        }
    )
    views = Integer()

    class Index:
        name = 'articles'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    @classmethod
    def from_article(cls, article: Article):
        
        tags_data = []
        for t in article.tags:
            if isinstance(t, dict):
                tags_data.append({
                    'name': t.get('name', ''),
                    'description': t.get('description', '')
                })
            else:
                
                tags_data.append({'name': str(t), 'description': ''})

        return cls(
            meta={'id': article.id},
            title=article.title,
            content=article.content,
            category=article.category,
            published_date=article.published_date,
            tags=tags_data,
            views=article.views
        )
