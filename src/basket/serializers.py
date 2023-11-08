from django.db.models import Sum
from rest_framework import serializers
from django.core.exceptions import ValidationError

from .models import Basket, BasketDetail, ClosedBasket, ClosedBasketDetail, ProductValidationCode
from src.coupon.models import LineCoupon


class BasketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Basket
        exclude = ["id", ]
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
        exclude = ["id", ]
        read_only_fields = ["slug", "payment_price", "payment_offer_percent", "payment_price_with_offer", "total_price",
                            "total_price_with_offer", ]


class AddToBasketSerializer(serializers.Serializer):
    line_coupon_slug = serializers.SlugField()
    basket_detail_count = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        data = self.initial_data
        line_coupon = LineCoupon.objects.filter(slug=data.get("line_coupon_slug"))
        if line_coupon.exists():
            line_coupon = line_coupon.first()
            if (data.get("basket_detail_count") + line_coupon.sell_count) > line_coupon.count:
                raise ValidationError({"basket_detail_count": "There is no more line coupons available!"})
            return super().validate(attrs)
        else:
            raise ValidationError({"line_coupon_slug": "Line coupon does not exists!"})


class ClosedBasketDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClosedBasketDetail
        exclude = ["id", ]


class ClosedBasketSerializer(serializers.ModelSerializer):
    product = ClosedBasketDetailSerializer(many=True)

    class Meta:
        model = ClosedBasket
        exclude = ["id", ]


class ClosedBasketDetailValidatorSerializer(serializers.Serializer):
    status_choices = (
        (2, "Verified"),
        (3, "Canceled"),
    )
    status = serializers.ChoiceField(choices=status_choices)


class ProductValidationCodeSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField("slug", read_only=True)
    closed_basket = serializers.SlugRelatedField("slug", read_only=True)

    class Meta:
        model = ProductValidationCode
        fields = "__all__"


class BytesField(serializers.Field):
    def to_internal_value(self, data):
        # Convert the string representation back to bytes
        try:
            byte_data = bytes.fromhex(data)
            return byte_data
        except ValueError:
            raise serializers.ValidationError("Invalid hexadecimal representation")

    def to_representation(self, obj):
        # Convert bytes to a hexadecimal string for serialization
        return obj.hex()


class QRCodeSerializer(serializers.Serializer):
    code = BytesField()
    used = serializers.BooleanField()


class QRCodeGetSerializer(serializers.Serializer):
    code = serializers.CharField()
    used = serializers.BooleanField()
