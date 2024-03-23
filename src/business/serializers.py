from rest_framework import serializers

from .models import Business, DepositRequest, CorporateRequest


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ["title", "slug", "admin", "description", "address"]
        read_only_fields = ["slug", ]


class DepositSerializer(serializers.ModelSerializer):
    def validate_sender(self):
        return self.context['request'].user

    class Meta:
        model = DepositRequest
        fields = '__all__'


class CorporateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorporateRequest
        fields = '__all__'

