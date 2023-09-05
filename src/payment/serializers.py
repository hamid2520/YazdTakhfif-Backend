from rest_framework import serializers

from src.payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["slug", "user", "basket", "total_price", "total_price_with_offer", "created_at"]
        read_only_fields = ["slug", "created_at"]
