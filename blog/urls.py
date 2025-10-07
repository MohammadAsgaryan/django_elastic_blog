from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet, ArticleAggregationAPIView, ArticleIncreaseViewsAPIView

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')

urlpatterns = [
    path('', include(router.urls)),
    path('articles/aggregation/', ArticleAggregationAPIView.as_view(), name='article-aggregation'),
    path('articles/<int:pk>/increase-views/', ArticleIncreaseViewsAPIView.as_view(), name='article-increase-views'),
]