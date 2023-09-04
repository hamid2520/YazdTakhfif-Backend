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
        super().save(**kwargs)
        count = self.instance.product.all().aggregate(Sum("count"))
        self.instance.count = count.get("count__sum")
        return self.instance


class BasketDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasketDetail
        fields = ["slug", "line_coupon", "count", "payment_price", "payment_offer_percent", "payment_price_with_offer",
                  "total_price", "total_price_with_offer", ]
        read_only_fields = ["slug", "payment_price", "payment_offer_percent", "payment_price_with_offer", "total_price",
                            "total_price_with_offer", ]
