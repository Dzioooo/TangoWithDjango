from rest_framework import serializers
from rango.models import Category

class CategoryGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CategoryPostPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ['slug', 'views', 'likes']
