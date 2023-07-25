from rest_framework import serializers
from src.business.serializers import BusinessSerializer
from .models import Category, Coupon, LineCoupon, LineCouponDetail


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("title", "slug", "parent", "level")


class CouponSerializer(serializers.ModelSerializer):
    business = BusinessSerializer()
    category = CategorySerializer(many=True)

    class Meta:
        model = Coupon
        fields = ("title", "slug", "business", "created", "expire_date", "category", "description", "terms_of_use")


class LineCouponDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineCouponDetail
        fields = ("price", "discount_percent", "sell_count")


class LineCouponSerializer(serializers.ModelSerializer):
    detail = LineCouponDetailSerializer()

    class Meta:
        model = LineCoupon
        fields = ("title", "detail", "is_main", "coupon")
