from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Article
from .documents import ArticleIndex

@receiver(post_save, sender=Article)
def index_article(sender, instance, **kwargs):
    doc = ArticleIndex.from_article(instance)
    doc.save()

@receiver(post_delete, sender=Article)
def delete_article(sender, instance, **kwargs):
    try:
        ArticleIndex.get(id=instance.id).delete()
    except Exception:
        pass
