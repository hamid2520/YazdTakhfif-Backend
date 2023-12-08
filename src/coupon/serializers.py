from django.db import IntegrityError
from django.db.models import Count, Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from src.business.serializers import BusinessSerializer
from .models import Category, Coupon, LineCoupon, Rate, Comment, CouponImage
from .exceptions import MaximumNumberOfDeletableObjectsError
from ..basket.models import BasketDetail
from ..business.models import Business
from ..users.models import User


class CategorySerializer(serializers.ModelSerializer):
    parent = serializers.SlugRelatedField(slug_field="slug", queryset=Category.objects.all())

    class Meta:
        model = Category
        fields = ["title", "slug", "parent"]
        read_only_fields = ["slug", ]


class CustomerCategorySerializer(serializers.ModelSerializer):
    parent = serializers.SlugRelatedField(slug_field="slug", queryset=Category.objects.all())
    sub_categories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["title", "slug", "parent", "sub_categories"]
        read_only_fields = ["slug", ]

    def get_sub_categories(self, obj: Category):
        sub_categories = obj.category_set.all()
        serializer = CategorySerializer(instance=sub_categories, many=True)
        return serializer.data


class CouponImageSerializer(serializers.ModelSerializer):
    coupon = serializers.SlugRelatedField(slug_field="slug", queryset=Coupon.objects.all())

    class Meta:
        model = CouponImage
        fields = "__all__"


class CouponSerializer(serializers.ModelSerializer):
    business = BusinessSerializer()
    category = CategorySerializer(many=True)
    rates_list = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    list_data = serializers.SerializerMethodField()
    comment_list = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = [
            "title", "slug", "business", "created", "expire_date", "category", "description", "terms_of_use",
            "coupon_rate", "rate_count", "rates_list", "images", "list_data", "comment_list"]

    def get_rates_list(self, obj: Coupon):
        rates_list: dict = obj.rate_set.all().aggregate(rate_1=Count("rate", filter=Q(rate=1)),
                                                        rate_2=Count("rate", filter=Q(rate=2)),
                                                        rate_3=Count("rate", filter=Q(rate=3)),
                                                        rate_4=Count("rate", filter=Q(rate=4)),
                                                        rate_5=Count("rate", filter=Q(rate=5)))

        rate_count = obj.rate_count

        for key, value in rates_list.items():
            if rate_count:
                rate_percent = round((value * 100) / rate_count)
                rates_list[key] = {
                    "count": value,
                    "percent": rate_percent
                }

            else:
                rates_list[key] = {
                    "count": 0,
                    "percent": 0
                }
        return list(rates_list.values())

    def get_images(self, obj: Coupon):
        images = obj.couponimage_set.all()
        images_list = [item.image.url for item in images]
        # serializer = CouponImageSerializer(instance=images, many=True)
        return images_list

    def get_list_data(self, obj: Coupon):
        main_line_coupon = obj.linecoupon_set.filter(is_main=True).first()
        serializer = LineCouponSerializer(instance=main_line_coupon)
        return serializer.data

    def get_comment_list(self, obj: Coupon):
        if self.context["view"].kwargs.get("slug"):
            comments = obj.comment_set.filter(verified=True)
            serializer = CommentSerializer(instance=comments, many=True)
            print(self.context["view"].kwargs.get("slug"))
            return serializer.data
        return []


class CouponCreateSerializer(serializers.ModelSerializer):
    business = serializers.SlugRelatedField(slug_field="slug", queryset=Business.objects.all())
    category = serializers.SlugRelatedField(slug_field="slug", queryset=Category.objects.all(), many=True)

    class Meta:
        model = Coupon
        fields = ["title", "business", "expire_date", "category", "description", "terms_of_use"]


class LineCouponSerializer(serializers.ModelSerializer):
    coupon = serializers.SlugRelatedField(slug_field="slug", queryset=Coupon.objects.all())

    def save(self, **kwargs):
        try:
            return super().save(**kwargs)
        except MaximumNumberOfDeletableObjectsError:
            raise ValidationError({"count": "There is no more coupon codes available for deletion!"})

    class Meta:
        model = LineCoupon
        fields = ["slug", "title", "coupon", "is_main", "count", "price", "offer_percent", "price_with_offer",
                  "sell_count"]
        read_only_fields = ["slug", "price_with_offer", "sell_count"]


class LineCouponShowSerializer(serializers.ModelSerializer):
    coupon = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    basket_detail_count = serializers.SerializerMethodField(read_only=True)
    in_stock = serializers.SerializerMethodField(read_only=True)
    max = serializers.SerializerMethodField(read_only=True)

    def get_in_stock(self, obj: LineCoupon):
        available_count = obj.count - obj.sell_count
        return True if available_count > 0 else False

    def get_basket_detail_count(self, obj: LineCoupon):
        basket_detail = BasketDetail.objects.filter(line_coupon_id=obj.id)
        if basket_detail.exists():
            return basket_detail.first().count
        return 0

    def get_max(self, obj: LineCoupon):
        available_count = obj.count - obj.sell_count
        return available_count

    class Meta:
        model = LineCoupon
        fields = ["slug", "title", "coupon", "is_main", "count", "price", "offer_percent", "price_with_offer",
                  "sell_count", "basket_detail_count", "in_stock", "max"]
        read_only_fields = ["slug", "price_with_offer", "sell_count"]


class RateSerializer(serializers.ModelSerializer):
    coupon = serializers.SlugRelatedField(slug_field="slug", queryset=Coupon.objects.all())

    class Meta:
        model = Rate
        fields = "__all__"
        read_only_fields = ["user", "coupon"]


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
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
        read_only_fields = ["id", "created_at"]
        extra_kwargs = {
            "user": {
                "required": False,
            },
            "coupon": {
                "required": False
            }
        }

    def get_user(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
