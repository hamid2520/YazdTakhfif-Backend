from django.db.models import Count, Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from src.business.serializers import BusinessSerializer
from .models import Category, Coupon, LineCoupon, Rate, Comment
from ..business.models import Business
from ..users.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["title", "slug", "parent", "level"]
        read_only_fields = ["slug", ]


class CouponSerializer(serializers.ModelSerializer):
    business = serializers.SlugRelatedField(slug_field="slug", queryset=Business.objects.all())
    category = serializers.SlugRelatedField(slug_field="slug", queryset=Category.objects.all(), many=True)
    rates_list = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = [
            "title", "slug", "business", "created", "expire_date", "category", "description", "terms_of_use",
            "coupon_rate", "rate_count", "rates_list"]

    def get_rates_list(self, obj: Coupon):
        if obj.rate_set.count() > 0:
            rates_list: dict = obj.rate_set.all().aggregate(rate_1=Count("rate", filter=Q(rate=1)),
                                                            rate_2=Count("rate", filter=Q(rate=2)),
                                                            rate_3=Count("rate", filter=Q(rate=3)),
                                                            rate_4=Count("rate", filter=Q(rate=4)),
                                                            rate_5=Count("rate", filter=Q(rate=5)))

            rate_count = obj.rate_count
            for key, value in rates_list.items():
                rate_percent = round((value * 100) / rate_count)
                rates_list[key] = {
                    "count": value,
                    "percent": rate_percent
                }
            return rates_list
        return None


class CouponCreateSerializer(serializers.ModelSerializer):
    business = serializers.SlugRelatedField(slug_field="slug", queryset=Business.objects.all())
    category = serializers.SlugRelatedField(slug_field="slug", queryset=Category.objects.all(), many=True)

    class Meta:
        model = Coupon
        fields = ["title", "business", "expire_date", "category", "description", "terms_of_use"]


class LineCouponSerializer(serializers.ModelSerializer):
    coupon = serializers.SlugRelatedField(slug_field="slug", queryset=Coupon.objects.all())

    class Meta:
        model = LineCoupon
        fields = ["slug", "title", "coupon", "is_main", "count", "price", "offer_percent", "price_with_offer",
                  "sell_count"]
        read_only_fields = ["slug", "price_with_offer", "sell_count"]


class RateSerializer(serializers.ModelSerializer):
    coupon = serializers.SlugRelatedField(slug_field="slug", read_only=True)

    class Meta:
        model = Rate
        fields = "__all__"
        read_only_fields = ["user", "coupon"]


class CommentSerializer(serializers.ModelSerializer):
    coupon = serializers.SlugRelatedField(slug_field="slug", queryset=Coupon.objects.all())

    def validate_user(self, value):
        request = self.context["request"]
        return request.user

    def validate_coupon(self, value):
        slug = self.context["kwargs"].get("slug")
        coupon = Coupon.objects.filter(slug=slug)
        if coupon.exists():
            return coupon.first()
        raise ValidationError("Coupon does not exists!")

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ["id", "user", "coupon", "created_at"]
        extra_kwargs = {
            "user": {
                "required": False,
            },
            "coupon": {
                "required": False
            }
        }
