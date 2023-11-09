from django.db.models import Count, Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from src.business.serializers import BusinessSerializer
from .models import Category, Coupon, LineCoupon, Rate, Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["title", "slug", "parent", "level"]
        read_only_fields = ["slug", ]


class CouponSerializer(serializers.ModelSerializer):
    business = BusinessSerializer()
    category = CategorySerializer(many=True)
    rates_list = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = [
            "title", "slug", "business", "created", "expire_date", "category", "description", "terms_of_use",
            "coupon_rate", "rate_count", "rates_list"]

    def get_rates_list(self, obj: Coupon):
        rates_list: dict = obj.rate_set.all().aggregate(rate_1=Count("rate", filter=Q(rate=1)),
                                                        rate_2=Count("rate", filter=Q(rate=2)),
                                                        rate_3=Count("rate", filter=Q(rate=3)),
                                                        rate_4=Count("rate", filter=Q(rate=4)),
                                                        rate_5=Count("rate", filter=Q(rate=5)))

        rate_count = obj.rate_count
        for key, value in rates_list.items():
            if rate_count :
                rate_percent = round((value * 100) / rate_count)
                rates_list[key] = {
                    "count": value,
                    "percent": rate_percent
                }

            else :
                rates_list[key] = {
                    "count": 0,
                    "percent": 0
                }  
                
        return rates_list


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


class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = "__all__"
        read_only_fields = ["user", "coupon"]


class CommentSerializer(serializers.ModelSerializer):

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
