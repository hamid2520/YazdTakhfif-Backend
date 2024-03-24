import jdatetime
from rest_framework import serializers

from .models import Business, DepositRequest, CorporateRequest


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ["title", "slug", "admin", "description", "address"]
        read_only_fields = ["slug", ]


class DepositSerializer(serializers.ModelSerializer):
    formatted_deposit_date = serializers.SerializerMethodField()
    formatted_requested_date = serializers.SerializerMethodField()

    def validate_sender(self):
        return self.context['request'].user

    class Meta:
        model = DepositRequest
        fields = ['requested_date', 'requested_price', 'status', 'deposit_date', 'document', 'sender',
                  'formatted_requested_date', 'formatted_deposit_date']

    def get_formatted_deposit_date(self, obj):
        if obj.deposit_date:
            datetime_field = jdatetime.datetime.fromgregorian(datetime=obj.deposit_date)
            return datetime_field.strftime("%Y/%m/%d")
        else:
            return None

    def get_formatted_requested_date(self, obj):
        if obj.requested_date:
            datetime_field = jdatetime.datetime.fromgregorian(datetime=obj.requested_date)
            return datetime_field.strftime("%Y/%m/%d")
        else:
            return None


class CorporateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorporateRequest
        fields = '__all__'
