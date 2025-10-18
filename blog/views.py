from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Article
from .serializers import (
    ArticleListSerializer,
    ArticleDetailSerializer,
    ArticleCreateSerializer,
    ArticleUpdateSerializer,
    ArticleSearchLogicSerializer,
    ArticleAggregationSerializer
)


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

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        result = ArticleCreateSerializer.bulk_create(request.data.get('articles', []))
        if result['errors']:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(ArticleDetailSerializer(result['created'], many=True).data)

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        result = ArticleUpdateSerializer.bulk_update(request.data.get('articles', []))
        if result['errors']:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(ArticleDetailSerializer(result['updated'], many=True).data)


class ArticleSearchAPIView(APIView):
    def get(self, request):
        serializer = ArticleSearchLogicSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        data = serializer.search()
        return Response(data)


class ArticleAggregationAPIView(APIView):
    def get(self, request):
        serializer = ArticleAggregationSerializer()
        data = serializer.aggregate()
        return Response(data)
