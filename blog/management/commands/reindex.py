from django.core.management.base import BaseCommand
from blog.documents import ArticleIndex
from blog.models import Article

class Command(BaseCommand):
    help = 'Reindex all articles into Elasticsearch'

    def handle(self, *args, **options):
        ArticleIndex.init()
        for a in Article.objects.all():
            ArticleIndex.from_article(a).save()
        self.stdout.write(self.style.SUCCESS('Reindex finished.'))
