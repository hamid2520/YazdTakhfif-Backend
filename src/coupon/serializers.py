from rest_framework import serializers

from .models import Category, Coupon, LineCoupon, Rate, Comment
from src.business.serializers import BusinessSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["title", "slug", "parent", "level"]
        read_only_fields = ["slug", ]


class CouponSerializer(serializers.ModelSerializer):
    business = BusinessSerializer()
    category = CategorySerializer(many=True)

    class Meta:
        model = Coupon
        fields = [
            "title", "slug", "business", "created", "expire_date", "category", "description", "terms_of_use",
            "coupon_rate", "rate_count"]


class CouponCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ["title", "business", "expire_date", "category", "description", "terms_of_use"]


class LineCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineCoupon
        fields = ["slug", "title", "coupon", "is_main", "count", "price", "offer_percent", "price_with_offer",
                  "sell_count"]
        read_only_fields = ["slug", "price_with_offer", "sell_count"]


class RateSerializer(serializers.Serializer):
    rate = serializers.IntegerField(min_value=0, max_value=5)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ["id", "user", "coupon", "created_at"]
