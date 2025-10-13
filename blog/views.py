from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from elasticsearch_dsl import Q, A
from elasticsearch import Elasticsearch
from .models import Article
from .serializers import (
    ArticleListSerializer,
    ArticleDetailSerializer,
    ArticleCreateSerializer,
    ArticleUpdateSerializer,
    ArticleSearchSerializer
)
from .documents import ArticleDocument, ArticleIndex


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().order_by('-published_date')

    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        elif self.action == 'retrieve':
            return ArticleDetailSerializer
        elif self.action == 'create':
            return ArticleCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ArticleUpdateSerializer
        return ArticleDetailSerializer

    @action(detail=True, methods=['post'])
    def increment_views(self, request, pk=None):
        article = self.get_object()
        amount = int(request.data.get('amount', 1))
        article.views += amount
        article.save()
        return Response({'views': article.views})

    @action(detail=False, methods=['post'])
    def bulk_reindex(self, request):
       
        ArticleIndex.init()
        for a in Article.objects.all():
            ArticleIndex.from_article(a).save()
        return Response({'status': 'reindexed'})

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        
        articles_data = request.data.get('articles', [])
        created = []
        for data in articles_data:
            serializer = ArticleCreateSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            article = serializer.save()
            
            ArticleIndex.from_article(article).save()
            created.append(ArticleDetailSerializer(article).data)
        return Response({'created': created}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """آپدیت چند مقاله به صورت bulk"""
        articles_data = request.data.get('articles', [])
        updated = []
        for data in articles_data:
            try:
                article = Article.objects.get(id=data.get('id'))
            except Article.DoesNotExist:
                continue
            serializer = ArticleUpdateSerializer(article, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            article = serializer.save()
            
            doc = ArticleDocument.get(id=article.id, ignore=404)
            if doc:
                doc.title = article.title
                doc.content = article.content
                doc.published_date = article.published_date
                doc.tags = article.tags
                doc.save()
            updated.append(ArticleDetailSerializer(article).data)
        return Response({'updated': updated}, status=status.HTTP_200_OK)



class ArticleSearchAPIView(APIView):
    def get(self, request):
        query = request.GET.get('q', '')
        s = ArticleDocument.search()
        if query:
            q = Q("multi_match", query=query, fields=["title", "content"])
            s = s.query(q)
        response = s.execute()
        results = []
        for hit in response:
            tag_list = [{"name": t.get('name', ''), "description": t.get('description','')} for t in hit.tags] if hit.tags else []
            results.append({
                "id": int(hit.meta.id),
                "title": hit.title,
                "content": hit.content,
                "tags": tag_list
            })
        serializer = ArticleSearchSerializer(results, many=True)
        return Response(serializer.data)



class ArticleAggregationAPIView(APIView):
    def get(self, request):
        s = ArticleIndex.search()
        tag_agg = A('terms', field='tags', size=10)
        s.aggs.bucket('by_tags', tag_agg)
        date_agg = A('date_histogram', field='published_date', calendar_interval='month', format='yyyy-MM-dd')
        s.aggs.bucket('by_month', date_agg)
        response = s.execute()
        result = {
            "by_tags": [{"tag": b.key, "count": b.doc_count} for b in response.aggregations.by_tags.buckets],
            "by_month": [{"month": b.key_as_string, "count": b.doc_count} for b in response.aggregations.by_month.buckets]
        }
        return Response(result)



class ArticleIncreaseViewsAPIView(APIView):
    def post(self, request, pk):
        es = Elasticsearch("http://localhost:9200")
        script_query = {
            "script": {"source": "ctx._source.views += params.count", "params": {"count": 1}},
            "query": {"term": {"_id": pk}}
        }
        response = es.update_by_query(index="articles", body=script_query, refresh=True)
        return Response(response, status=status.HTTP_200_OK)
