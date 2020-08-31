from django.db import models
from django_mysql.models import JSONField

class Movies(models.Model):
    popularity = models.FloatField(null=True, blank=True)
    director = models.CharField(max_length=256)
    genre = JSONField(null=True, blank=True)
    imdb_score = models.FloatField(null=True, blank=True)
    name = models.TextField()
    STATUS_CHOICES = (
        ('active', 'active'),
        ('deleted', 'deleted')
    )
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default='active')

    class Meta:
        db_table = 'movies'