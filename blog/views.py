from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Article
from .serializers import ArticleSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import Search, Q
from .documents import ArticleDocument 
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from elasticsearch import Elasticsearch
from .documents import ArticleIndex
from elasticsearch_dsl import A

    
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().order_by('-published_date')
    serializer_class = ArticleSerializer

    @action(detail=True, methods=['post'])
    def increment_views(self, request, pk=None):
        article = self.get_object()
        amount = int(request.data.get('amount', 1))
        article.views += amount
        article.save()
        return Response({'views': article.views})

    @action(detail=False, methods=['post'])
    def bulk_reindex(self, request):
        from .documents import ArticleIndex
        ArticleIndex.init()
        from .models import Article
        for a in Article.objects.all():
            ArticleIndex.from_article(a).save()
        return Response({'status': 'reindexed'})
    
    
class ArticleCreateAPIView(generics.CreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def perform_create(self, serializer):
        article = serializer.save()
       
        doc = ArticleDocument(
            meta={'id': article.id},
            title=article.title,
            content=article.content,
            published_date=article.published_at,
            tags=article.tags
        )
        doc.save()


class ArticleSearchAPIView(APIView):
    def get(self, request):
        query = request.GET.get('q', '')

        s = ArticleDocument.search()

        if query:
            q = Q("multi_match", query=query, fields=["title", "content"])
            s = s.query(q)

        response = s.execute()
        results = [
            {
                "id": hit.meta.id,
                "title": hit.title,
                "content": hit.content,
                "tags": hit.tags,
            }
            for hit in response
        ]
        return Response(results)
    
    
class ArticleUpdateAPIView(generics.UpdateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    lookup_field = 'pk'

    def perform_update(self, serializer):
        article = serializer.save()

        
        doc = ArticleDocument.get(id=article.id, ignore=404)
        if doc:
            doc.title = article.title
            doc.content = article.content
            doc.published_date = article.published_at
            doc.tags = article.tags
            doc.save()
            
class ArticleDeleteAPIView(generics.DestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    lookup_field = 'pk'

    def perform_destroy(self, instance):
        
        try:
            doc = ArticleIndex.get(id=instance.id, ignore=404)
            doc.delete()
        except Exception as e:
            print(f"ES delete error: {e}")

        
        instance.delete()           
        
        
class ArticleAggregationAPIView(APIView):
    def get(self, request):
        
        s = ArticleIndex.search()
        
        
        tag_agg = A('terms', field='tags', size=10)
        s.aggs.bucket('by_tags', tag_agg)
        
        
        date_agg = A('date_histogram', field='published_date', calendar_interval='month', format='yyyy-MM-dd')
        s.aggs.bucket('by_month', date_agg)
        response = s.execute()

        result = {
            "by_tags": [
                {"tag": b.key, "count": b.doc_count}
                for b in response.aggregations.by_tags.buckets
            ],
            "by_month": [
                {"month": b.key_as_string, "count": b.doc_count}
                for b in response.aggregations.by_month.buckets
            ]
        }

        return Response(result)
    
    
class ArticleIncreaseViewsAPIView(APIView):
    def post(self, request, pk):
        es = Elasticsearch("http://localhost:9200")
        script_query = {
            "script": {
                "source": "ctx._source.views += params.count",
                "params": {"count": 1}
            },
            "query": {
                "term": {"_id": pk}
            }
        }

        response = es.update_by_query(
            index="articles",
            body=script_query,
            refresh=True
        )

        return Response(response, status=status.HTTP_200_OK)