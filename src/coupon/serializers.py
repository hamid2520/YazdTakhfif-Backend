from rest_framework import serializers

from .models import Category, Coupon, LineCoupon
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
            "title", "slug", "business", "created", "expire_date", "category", "description", "terms_of_use"]


class CouponCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ["title", "business", "expire_date", "category", "description", "terms_of_use"]


class LineCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineCoupon
        fields = "__all__"
        read_only_fields = ["id", "final_price", "bought_count"]
