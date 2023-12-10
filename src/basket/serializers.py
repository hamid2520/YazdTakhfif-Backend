import jdatetime

from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from .models import Basket, BasketDetail, ClosedBasket, ClosedBasketDetail, ProductValidationCode
from src.coupon.models import LineCoupon, Coupon, CouponImage
from src.coupon.serializers import LineCouponSerializer


class BasketDetailSerializer(serializers.ModelSerializer):
    line_coupon = serializers.SlugRelatedField(slug_field="slug", queryset=LineCoupon.objects.all())

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
    line_coupon = serializers.SlugRelatedField(slug_field="title", read_only=True)
    line_coupon_slug = serializers.SlugField(read_only=True,source="line_coupon.slug")
    in_stock = serializers.SerializerMethodField()
    imagesrc = serializers.SerializerMethodField()
    max = serializers.SerializerMethodField()
    min = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    def get_in_stock(self, obj: BasketDetail):
        line_coupon = obj.line_coupon
        available_count = line_coupon.count - line_coupon.sell_count
        return True if available_count > 0 else False

    def get_imagesrc(self, obj: BasketDetail):
        image: CouponImage = CouponImage.objects.filter(coupon_id=obj.line_coupon.coupon.id).first()
        if image:
            return image.image.url
        return ""

    def get_max(self, obj: BasketDetail):
        line_coupon = obj.line_coupon
        available_count = line_coupon.count - line_coupon.sell_count
        return available_count

    def get_min(self, obj: BasketDetail):
        return 1 if self.get_in_stock(obj) else 0

    def get_price(self, obj: BasketDetail):
        line_coupon = obj.line_coupon
        return {
            "price": line_coupon.price,
            "discounted_price": line_coupon.price_with_offer,
            "discounted_percentage": line_coupon.offer_percent,
            "total_price": obj.total_price,
            "total_price_with_offer": obj.total_price_with_offer,
        }

    class Meta:
        model = BasketDetail
        exclude = ["id", "payment_price", "payment_price_with_offer", "payment_offer_percent", "total_price",
                   "total_price_with_offer"]
        read_only_fields = ["slug", "payment_price", "payment_offer_percent", "payment_price_with_offer", "total_price",
                            "total_price_with_offer", ]


class BasketSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(slug_field="slug", read_only=True, many=True)
    formatted_created_at = serializers.SerializerMethodField()
    formatted_payment_datetime = serializers.SerializerMethodField()

    def get_formatted_created_at(self, obj):
        datetime_field = jdatetime.datetime.fromgregorian(datetime=obj.created_at)
        return datetime_field.strftime("%Y/%m/%d %H:%M:%S")

    def get_formatted_payment_datetime(self, obj):
        try:
            datetime_field = jdatetime.datetime.fromgregorian(datetime=obj.payment_datetime)
            return datetime_field.strftime("%Y/%m/%d %H:%M:%S")
        except ValueError:
            return None

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


class BasketShowSerializer(serializers.ModelSerializer):
    product = BasketDetailShowSerializer(read_only=True, many=True)
    formatted_created_at = serializers.SerializerMethodField()
    formatted_payment_datetime = serializers.SerializerMethodField()

    def get_formatted_created_at(self, obj):
        datetime_field = jdatetime.datetime.fromgregorian(datetime=obj.created_at)
        return datetime_field.strftime("%Y/%m/%d %H:%M:%S")

    def get_formatted_payment_datetime(self, obj):
        try:
            datetime_field = jdatetime.datetime.fromgregorian(datetime=obj.payment_datetime)
            return datetime_field.strftime("%Y/%m/%d %H:%M:%S")
        except ValueError:
            return None

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
    basket_detail_count = serializers.IntegerField(min_value=0)
    basket = serializers.SerializerMethodField(read_only=True)

    def get_basket(self, obj):
        basket = Basket.objects.get(id=self.context.get("basket_id"))
        serializer = BasketShowSerializer(instance=basket)
        return serializer.data

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
    formatted_created_at = serializers.SerializerMethodField()
    formatted_payment_datetime = serializers.SerializerMethodField()

    def get_formatted_created_at(self, obj):
        datetime_field = jdatetime.datetime.fromgregorian(datetime=obj.created_at)
        return datetime_field.strftime("%Y/%m/%d %H:%M:%S")

    def get_formatted_payment_datetime(self, obj):
        datetime_field = jdatetime.datetime.fromgregorian(datetime=obj.payment_datetime)
        return datetime_field.strftime("%Y/%m/%d %H:%M:%S")

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
    formatted_created = serializers.SerializerMethodField()
    formatted_expire_date = serializers.SerializerMethodField()

    def get_formatted_created(self, obj):
        datetime_field = jdatetime.datetime.fromgregorian(datetime=obj.created)
        return datetime_field.strftime("%Y/%m/%d %H:%M:%S")

    def get_formatted_expire_date(self, obj):
        datetime_field = jdatetime.datetime.fromgregorian(datetime=obj.expire_date)
        return datetime_field.strftime("%Y/%m/%d %H:%M:%S")

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


class ProductValidationCodeShowSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField("title", read_only=True)
    closed_basket = serializers.SerializerMethodField()

    def get_closed_basket(self, obj):
        datetime_obj = jdatetime.datetime.fromgregorian(datetime=obj.closed_basket.payment_datetime)
        return f"{obj.closed_basket.user.username}({datetime_obj.strftime('%Y/%m/%d %H:%M:%S')})"

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
