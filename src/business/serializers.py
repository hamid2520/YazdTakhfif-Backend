from rest_framework import serializers

from .models import Business


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ["title", "slug", "admin", "description", "address"]
        read_only_fields = ["slug", ]
