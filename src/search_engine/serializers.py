from rest_framework import serializers


class SearchEngineApiSerializer(serializers.Serializer):
    title = serializers.CharField()
    slug = serializers.SlugField()
    model_name = serializers.CharField()