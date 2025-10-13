from rest_framework import serializers
from .models import Article


class TagSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)


class ArticleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'category', 'published_date', 'views']

class ArticleDetailSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = Article
        fields = '__all__'

class ArticleCreateSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = Article
        fields = ['title', 'content', 'category', 'tags']
        
        
    def validate_tags(self, value):
        for tag in value:
            if 'name' not in tag or not tag['name']:
                raise serializers.ValidationError("Each tag must have a name.")
        return value
    
    
class ArticleUpdateSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = Article
        fields = ['title', 'content', 'category', 'tags']


class ArticleSearchSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    content = serializers.CharField()
    tags = TagSerializer(many=True)
