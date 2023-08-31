from rest_framework import serializers

from .models import Basket,BasketDetail


class BasketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Basket
        fields = ["slug", "user", "product", "created_at", "payment_datetime", "is_paid", "count", "total_price",
                  "total_offer_percent", "total_price_with_offer"]
        read_only_fields = ["slug", "created_at", "payment_datetime", "is_paid", "count", "total_price",
                            "total_offer_percent", "total_price_with_offer", ]


class BasketDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasketDetail
        fields = ["slug", "line_coupon", "count", "payment_price", "payment_offer_percent", "payment_price_with_offer",
                  "final_price", "final_price_with_offer", ]
        read_only_fields = ["slug", "payment_price", "payment_offer_percent", "payment_price_with_offer", "final_price",
                            "final_price_with_offer", ]


