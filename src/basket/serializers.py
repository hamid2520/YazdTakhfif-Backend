from django.db.models import Sum
from rest_framework import serializers

from .models import Basket


class BasketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Basket
        fields = "__all__"
        read_only_fields = ["id", "created_at", "payment_datetime", "is_paid", "count", "total_price",
                            "total_offer_percent", "total_price_with_offer", ]

    def save(self, **kwargs):
        super().save(**kwargs)
        count = self.instance.product.all().aggregate(Sum("count"))
        self.instance.count = count.get("count__sum")
        return self.instance
