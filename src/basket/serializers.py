from django.db.models import Sum
from rest_framework import serializers

from .models import Basket, BasketDetail


class BasketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Basket
        fields = ["slug", "user", "product", "created_at", "payment_datetime", "is_paid", "count", "total_price",
                  "total_offer_percent", "total_price_with_offer"]
        read_only_fields = ["slug", "created_at", "payment_datetime", "is_paid", "count", "total_price",
                            "total_offer_percent", "total_price_with_offer", ]

    def save(self, **kwargs):
        user = self.validated_data.get("user")
        basket = Basket.objects.filter(user_id=user.id, is_paid=False)
        if basket.exists():
            self.instance = basket.first()
        super().save(**kwargs)
        return self.instance


class BasketDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasketDetail
        fields = ["slug", "line_coupon", "count", "payment_price", "payment_offer_percent", "payment_price_with_offer",
                  "total_price", "total_price_with_offer", ]
        read_only_fields = ["slug", "payment_price", "payment_offer_percent", "payment_price_with_offer", "total_price",
                            "total_price_with_offer", ]


class AddToBasketSerializer(serializers.Serializer):
    line_coupon_slug = serializers.SlugField()
    basket_detail_count = serializers.IntegerField(min_value=1)
