from rest_framework import serializers

from .models import Category, Coupon, LineCoupon
from src.business.serializers import BusinessSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "title", "slug", "parent", "level")


class LineCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineCoupon
        fields = "__all__"


class CouponSerializer(serializers.ModelSerializer):
    business = BusinessSerializer()
    category = CategorySerializer(many=True)

    class Meta:
        model = Coupon
        fields = (
            "id", "title", "slug", "business", "created", "expire_date", "category", "description", "terms_of_use")


class CouponCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ("title", "business", "expire_date", "category", "description", "terms_of_use")
