from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=100)
    tags = models.JSONField(default=list)
    published_date = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0) 

    def __str__(self):
        return self.title
