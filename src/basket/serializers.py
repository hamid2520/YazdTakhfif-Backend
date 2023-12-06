from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from .models import Basket, BasketDetail, ClosedBasket, ClosedBasketDetail, ProductValidationCode
from src.coupon.models import LineCoupon, Coupon, CouponImage
from src.coupon.serializers import LineCouponSerializer


class BasketDetailSerializer(serializers.ModelSerializer):
    line_coupon = serializers.SlugRelatedField(slug_field="title", read_only=True)

    def validate(self, attrs):
        data = super().validate(attrs)
        line_coupon = LineCoupon.objects.get(id=data.get("line_coupon").id)
        if (int(data.get("count")) + line_coupon.sell_count) > line_coupon.count:
            raise ValidationError({"basket_detail_count": "There is no more line coupons available!"})
        return attrs

    class Meta:
        model = BasketDetail
        exclude = ["id", ]
        read_only_fields = ["slug", "payment_price", "payment_offer_percent", "payment_price_with_offer", "total_price",
                            "total_price_with_offer", ]


class BasketDetailShowSerializer(serializers.ModelSerializer):
    line_coupon = LineCouponSerializer(read_only=True)
    imagesrc = serializers.SerializerMethodField()

    def get_imagesrc(self, obj: BasketDetail):
        image: CouponImage = CouponImage.objects.filter(coupon_id=obj.line_coupon.coupon.id).first()
        return image.image.url

    class Meta:
        model = BasketDetail
        exclude = ["id", ]
        read_only_fields = ["slug", "payment_price", "payment_offer_percent", "payment_price_with_offer", "total_price",
                            "total_price_with_offer", ]


class BasketSerializer(serializers.ModelSerializer):
    product = BasketDetailShowSerializer(many=True)

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


class AddToBasketSerializer(serializers.Serializer):
    line_coupon_slug = serializers.SlugField()
    basket_detail_count = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        data = super().validate(attrs)
        line_coupon = LineCoupon.objects.filter(slug=data.get("line_coupon_slug"))
        if line_coupon.exists():
            line_coupon = line_coupon.first()
            if (int(data.get("basket_detail_count")) + line_coupon.sell_count) > line_coupon.count:
                raise ValidationError({"basket_detail_count": "There is no more line coupons available!"})
            return super().validate(attrs)
        else:
            raise ValidationError({"line_coupon_slug": "Line coupon does not exists!"})


class ClosedBasketDetailSerializer(serializers.ModelSerializer):
    line_coupon = serializers.SlugRelatedField(slug_field="title", read_only=True)

    class Meta:
        model = ClosedBasketDetail
        exclude = ["id", ]


class ClosedBasketSerializer(serializers.ModelSerializer):
    product = ClosedBasketDetailSerializer(many=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = ClosedBasket
        exclude = ["id", ]

    def get_status(self, obj):
        try:
            return ClosedBasket.status_choices[int(obj.status) - 1][1]
        except:
            return 'نامشخص'


class LineCouponWithCodesSerializer(serializers.ModelSerializer):
    coupon_codes = serializers.SerializerMethodField()

    def get_coupon_codes(self, obj: LineCoupon):
        user_id = self.context.get("user_id")
        coupon_codes = ProductValidationCode.objects.filter(product_id=obj.id, closed_basket__user_id=user_id)
        serializer = ProductValidationCodeSerializer(instance=coupon_codes, many=True)
        return serializer.data

    class Meta:
        model = LineCoupon
        exclude = ["id", ]


class UserBoughtCodesSerializer(serializers.ModelSerializer):
    line_coupons = serializers.SerializerMethodField()
    days_left = serializers.SerializerMethodField()
    business_title = serializers.CharField()
    address = serializers.CharField()
    phone_number = serializers.CharField()

    def get_line_coupons(self, obj):
        user_id = self.context.get("user_id")
        line_coupons = LineCoupon.objects.filter(coupon_id=obj.id, closedbasketdetail__closedbasket__status=3,
                                                 closedbasketdetail__closedbasket__user_id=user_id)
        serializer = LineCouponWithCodesSerializer(instance=line_coupons, many=True, context={"user_id": user_id})
        return serializer.data

    def get_days_left(self, obj):
        time_now = timezone.now()
        if obj.days_left > time_now:
            return (obj.days_left - timezone.now()).days
        else:
            return -1

    class Meta:
        model = Coupon
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
