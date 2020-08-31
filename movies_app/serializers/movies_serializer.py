from rest_framework import serializers
from movies_app.model.movies import Movies
from movies_app import models


class MoviesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Movies
        fields = "__all__"
