from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Payment
from src.basket.models import Basket, BasketDetail


class PaymentSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = self.initial_data
        basket = Basket.objects.filter(id=data.get("basket"))
        if basket.exists():
            basket = basket.first()
            for product in basket.product.all():
                if (product.count + product.line_coupon.sell_count) > product.line_coupon.count:
                    error = f"Basket({product.line_coupon.title})`s count is more than available count!"
                    raise ValidationError({"basket": error})
            return super().validate(attrs)
        raise ValidationError({"basket": "Basket does not exists!"})

    class Meta:
        model = Payment
        fields = ["slug", "user", "basket", "total_price", "total_price_with_offer", "created_at"]
        read_only_fields = ["slug", "created_at"]
