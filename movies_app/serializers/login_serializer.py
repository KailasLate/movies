from rest_framework import serializers
from movies_app.model.users import User
from movies_app import models


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = "__all__"
