import jdatetime
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Count, Q, Sum
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from src.business.serializers import BusinessSerializer
from .exceptions import MaximumNumberOfDeletableObjectsError
from .models import Category, Coupon, LineCoupon, Rate, Comment, CouponImage
from ..basket.models import BasketDetail, Basket
from ..business.models import Business


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
    formatted_created = serializers.SerializerMethodField()
    formatted_expire_date = serializers.SerializerMethodField()
    available_coupon_count = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = [
            "title", "slug", "business", "created", "expire_date", "category", "description", "terms_of_use",
            "coupon_rate", "rate_count", "rates_list", "images", "list_data", "comment_list", "formatted_created",
            "formatted_expire_date", "available_coupon_count"]

    def get_formatted_created(self, obj):
        datetime_field = jdatetime.datetime.fromgregorian(datetime=obj.created)
        return datetime_field.strftime("%Y/%m/%d %H:%M:%S")

    def get_formatted_expire_date(self, obj):
        datetime_field = jdatetime.datetime.fromgregorian(datetime=obj.expire_date)
        return datetime_field.strftime("%Y/%m/%d %H:%M:%S")

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
        images_list = [{"id": item.id, "url": item.image.url} for item in images]
        # serializer = CouponImageSerializer(instance=images, many=True)
        return images_list

    def get_list_data(self, obj: Coupon):
        main_line_coupon = obj.linecoupon_set.filter(is_main=True).first()
        serializer = LineCouponSerializer(instance=main_line_coupon)
        return serializer.data

    def get_comment_list(self, obj: Coupon):
        if self.context["view"].kwargs.get("slug"):
            comments = obj.comment_set.filter(verified=True, parent__isnull=True)
            serializer = CustomerCommentSerializer(instance=comments, many=True)
            return serializer.data
        return []

    def get_available_coupon_count(self, obj: Coupon):
        counts = obj.linecoupon_set.all().aggregate(count=Sum("count"), bought_count=Sum("sell_count"))
        return counts["count"] - counts["bought_count"] if counts["count"] else 0


class CouponCreateSerializer(serializers.ModelSerializer):
    business = serializers.SlugRelatedField(slug_field="title", required=False, queryset=Business.objects.all())
    category = serializers.SlugRelatedField(slug_field="slug", queryset=Category.objects.all(), many=True)
    formatted_created = serializers.SerializerMethodField()
    formatted_expire_date = serializers.SerializerMethodField()
    expire_date = serializers.DateField()

    def get_formatted_created(self, obj):
        datetime_field = jdatetime.datetime.fromgregorian(datetime=obj.created)
        return datetime_field.strftime("%Y/%m/%d %H:%M:%S")

    def get_formatted_expire_date(self, obj):
        datetime_field = jdatetime.datetime.fromgregorian(datetime=obj.expire_date)
        return datetime_field.strftime("%Y/%m/%d %H:%M:%S")

    def validate_category(self, value):
        for category in value:
            if not category.parent:
                raise ValidationError("!شما نمی توانید دسته بندی اصلی را انتخاب کنید")
        return value

    def save(self, **kwargs):
        user_id = self.context.get('request').user.id
        if 'business' not in self.validated_data:
            business = Business.objects.filter(admin_id=user_id)
            if not business.exists():
                raise ValidationError({"business": "Business not found!"})
            business = business.first()
            self.validated_data["business"] = business
        return super().save(**kwargs)

    class Meta:
        model = Coupon
        fields = ["slug", "title", "business", "expire_date", "category", "description", "terms_of_use",
                  "formatted_created",
                  "formatted_expire_date"]
        read_only_fields = ['slug', ]


class LineCouponSerializer(serializers.ModelSerializer):
    coupon = serializers.SlugRelatedField(slug_field="slug", queryset=Coupon.objects.all())

    def validate(self, attrs):
        if attrs["commission"] >= attrs["price_with_offer"]:
            raise ValidationError({"commission": "Commission must be lower than price with offer!"})

    def save(self, **kwargs):
        try:
            return super().save(**kwargs)
        except MaximumNumberOfDeletableObjectsError:
            raise ValidationError({"count": "There is no more coupon codes available for deletion!"})
        except DjangoValidationError:
            raise ValidationError({"is_main": "Just one line coupon can be main!"})

    class Meta:
        model = LineCoupon
        fields = ["slug", "title", "coupon", "is_main", "count", "price", "offer_percent", "price_with_offer",
                  "sell_count", "commission"]
        read_only_fields = ["slug", "offer_percent", "sell_count"]


class LineCouponShowSerializer(serializers.ModelSerializer):
    coupon = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    basket_detail_count = serializers.SerializerMethodField(read_only=True)
    in_stock = serializers.SerializerMethodField(read_only=True)
    max = serializers.SerializerMethodField(read_only=True)
    line_coupon_count = serializers.SerializerMethodField(read_only=True)
    days_left = serializers.SerializerMethodField(read_only=True)

    def get_days_left(self, obj):
        time_now = timezone.now().date()
        if obj.coupon.expire_date > time_now:
            return (obj.coupon.expire_date - time_now).days
        else:
            return -1

    def get_in_stock(self, obj: LineCoupon):
        available_count = obj.count - obj.sell_count
        return True if available_count > 0 else False

    def get_basket_detail_count(self, obj: LineCoupon):
        if self.context['request'].user.is_anonymous:
            basket_slug = self.context.get('basket_slug')
            if basket_slug:
                basket_detail = BasketDetail.objects.filter(line_coupon_id=obj.id, basket__slug=basket_slug)
                if basket_detail.exists():
                    return basket_detail.first().count
            return 0
        basket_detail = BasketDetail.objects.filter(line_coupon_id=obj.id,
                                                    basket__user__id=self.context['request'].user.id)
        if basket_detail.exists():
            return basket_detail.first().count
        return 0

    def get_max(self, obj: LineCoupon):
        available_count = obj.count - obj.sell_count
        return available_count

    def get_line_coupon_count(self, obj: LineCoupon):
        try:
            if self.context['request'].user.is_anonymous:
                basket_slug = self.context.get('basket_slug')
                if basket_slug:
                    basket_detail = BasketDetail.objects.filter(line_coupon_id=obj.id, basket__slug=basket_slug)
                    if basket_detail.exists():
                        return basket_detail.first().count
                return 0
            else:
                basket_detail = BasketDetail.objects.filter(line_coupon_id=obj.id,
                                                            basket__user=self.context['request'].user).first()
                return basket_detail.count
        except:
            return 0

    class Meta:
        model = LineCoupon
        fields = ["slug", "title", "coupon", "is_main", "count", "price", "offer_percent", "price_with_offer",
                  "sell_count", "basket_detail_count", "in_stock", "max", "line_coupon_count", "days_left",
                  "commission"]
        read_only_fields = ["slug", "price_with_offer", "sell_count"]


class RateSerializer(serializers.ModelSerializer):
    # coupon = serializers.SlugRelatedField(slug_field="slug", queryset=Coupon.objects.all())

    class Meta:
        model = Rate
        fields = "__all__"
        read_only_fields = ["user", "coupon"]


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    coupon = serializers.SlugRelatedField(slug_field="slug", queryset=Coupon.objects.all())
    formatted_created_at = serializers.SerializerMethodField()

    def get_formatted_created_at(self, obj):
        datetime_field = jdatetime.datetime.fromgregorian(datetime=obj.created_at)
        return datetime_field.strftime("%Y/%m/%d %H:%M:%S")

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
        user = obj.user
        return f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else user.username


class CustomerCommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField(read_only=True)
    coupon = serializers.SlugRelatedField(slug_field="slug", queryset=Coupon.objects.all())
    formatted_created_at = serializers.SerializerMethodField()
    sub_comment = serializers.SerializerMethodField()
    rate = serializers.SerializerMethodField()

    def get_user(self, obj):
        name_valid = bool(obj.user.first_name and obj.user.last_name)
        return f"{obj.user.first_name} {obj.user.last_name}" if name_valid else obj.user.username

    def get_profile_picture(self, obj):
        if obj.user.profile_picture:
            return obj.user.profile_picture.url
        else:
            return ""

    def get_formatted_created_at(self, obj):
        datetime_field = jdatetime.datetime.fromgregorian(datetime=obj.created_at)
        return datetime_field.strftime("%Y/%m/%d %H:%M:%S")

    def get_sub_comment(self, obj):
        sub_comment = CustomerCommentSerializer(instance=obj.comment_set.filter(verified=True), many=True)
        return sub_comment.data

    def get_rate(self, obj: Comment):
        user_id = obj.user.id
        rate = Rate.objects.filter(coupon=obj.coupon, user_id=user_id).first()
        return rate.rate if rate else 0

    class Meta:
        model = Comment
        fields = "__all__"
