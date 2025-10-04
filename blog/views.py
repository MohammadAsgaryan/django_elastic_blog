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
