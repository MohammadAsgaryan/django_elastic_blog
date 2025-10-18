from django.db import transaction
from rest_framework import serializers
from .models import Article, Tag
from .documents import ArticleDocument, ArticleIndex
import logging

logger = logging.getLogger(__name__)

# --------------------- Tag Serializer ---------------------
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'description']


# --------------------- Article Serializers ---------------------
class _TagMixin:
    """Helper برای مدیریت تگ‌ها"""

    def _process_tags(self, tags_data):
        tag_objs = []
        for tag in tags_data:
            tag_obj, created = Tag.objects.get_or_create(
                name=tag['name'],
                defaults={'description': tag.get('description', '')}
            )
            # بروزرسانی description اگر لازم بود
            if not created and tag.get('description') and tag_obj.description != tag['description']:
                tag_obj.description = tag['description']
                tag_obj.save(update_fields=['description'])
            tag_objs.append(tag_obj)
        return tag_objs


class ArticleCreateSerializer(_TagMixin, serializers.ModelSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = Article
        fields = ['title', 'content', 'category', 'tags']

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        with transaction.atomic():
            article = Article.objects.create(**validated_data)
            if tags_data:
                article.tags.set(self._process_tags(tags_data))
            ArticleIndex.from_article(article).save()
        return article

    @classmethod
    def bulk_create(cls, articles_data):
        created_articles = []
        errors = []
        with transaction.atomic():
            for idx, data in enumerate(articles_data):
                serializer = cls(data=data)
                try:
                    serializer.is_valid(raise_exception=True)
                    article = serializer.save()
                    created_articles.append(article)
                except serializers.ValidationError as e:
                    errors.append({'index': idx, 'errors': e.detail})
        for article in created_articles:
            ArticleIndex.from_article(article).save()
        return {'created': created_articles, 'errors': errors}


class ArticleUpdateSerializer(_TagMixin, serializers.ModelSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = Article
        fields = ['title', 'content', 'category', 'tags']

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        with transaction.atomic():
            if tags_data is not None:
                instance.tags.set(self._process_tags(tags_data))
            instance.save()
            ArticleIndex.from_article(instance).save()
        return instance

    @classmethod
    def bulk_update(cls, articles_data):
        updated_articles = []
        errors = []
        with transaction.atomic():
            for idx, data in enumerate(articles_data):
                article_id = data.get('id')
                if not article_id:
                    errors.append({'index': idx, 'error': 'id missing'})
                    continue
                try:
                    article = Article.objects.get(id=article_id)
                except Article.DoesNotExist:
                    errors.append({'index': idx, 'error': f'article id={article_id} not found'})
                    continue
                serializer = cls(article, data=data, partial=True)
                try:
                    serializer.is_valid(raise_exception=True)
                    updated = serializer.save()
                    updated_articles.append(updated)
                except serializers.ValidationError as e:
                    errors.append({'index': idx, 'id': article_id, 'errors': e.detail})
        for article in updated_articles:
            ArticleIndex.from_article(article).save()
        return {'updated': updated_articles, 'errors': errors}


class ArticleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'category', 'published_date', 'views']


class ArticleDetailSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = '__all__'


class ArticleSearchSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    content = serializers.CharField()
    tags = TagSerializer(many=True)


class ArticleSearchLogicSerializer(serializers.Serializer):
    query = serializers.CharField(required=False, allow_blank=True)

    def search(self):
        query = self.validated_data.get('query', '')
        s = ArticleDocument.search()
        if query:
            from elasticsearch_dsl import Q
            s = s.query(Q("multi_match", query=query, fields=["title", "content"]))
        response = s.execute()
        results = []
        for hit in response:
            tags_list = [{"name": t.get('name',''), "description": t.get('description','')} for t in hit.tags] if hit.tags else []
            results.append({
                "id": int(hit.meta.id),
                "title": hit.title,
                "content": hit.content,
                "tags": tags_list
            })
        serializer = ArticleSearchSerializer(results, many=True)
        return serializer.data


class ArticleAggregationSerializer(serializers.Serializer):
    def aggregate(self):
        s = ArticleIndex.search()
        from elasticsearch_dsl import A
        tag_agg = A('terms', field='tags.name.keyword', size=10)
        s.aggs.bucket('by_tags', tag_agg)
        date_agg = A('date_histogram', field='published_date', calendar_interval='month', format='yyyy-MM-dd')
        s.aggs.bucket('by_month', date_agg)
        response = s.execute()
        result = {
            "by_tags": [{"tag": b.key, "count": b.doc_count} for b in response.aggregations.by_tags.buckets],
            "by_month": [{"month": b.key_as_string, "count": b.doc_count} for b in response.aggregations.by_month.buckets]
        }
        return result
