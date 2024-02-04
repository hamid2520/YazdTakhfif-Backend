from django.db.models import Sum
from django.utils import timezone
from jdatetime import datetime
from rest_framework import serializers

from .models import *
from ..basket.models import ProductValidationCode
from ..basket.serializers import ProductValidationCodeSerializer
from ..business.models import Business
from ..coupon.models import LineCoupon, Coupon
from ..utils.get_bool import get_boolean


class LineCouponWithCodesSerializer(serializers.ModelSerializer):
    coupon_codes = serializers.SerializerMethodField()
    coupon = serializers.SlugRelatedField(slug_field="title", read_only=True)
    total_sell_price = serializers.SerializerMethodField()
    total_sell_count = serializers.SerializerMethodField()

    def get_coupon_codes(self, obj: LineCoupon):
        user_id = self.context.get("user_id")
        coupon_codes = (ProductValidationCode.objects.
                        filter(product_id=obj.id,
                               closed_basket__product__line_coupon__coupon__business__admin_id=user_id))
        serializer = ProductValidationCodeSerializer(instance=coupon_codes, many=True)
        return serializer.data

    def get_total_sell_price(self, obj: LineCoupon):
        total_sell_price = obj.closedbasketdetail_set.filter(status=2).aggregate(total=Sum('total_price_with_offer'))[
            "total"]
        return total_sell_price if total_sell_price else 0

    def get_total_sell_count(self, obj: LineCoupon):
        total_sell_count = obj.closedbasketdetail_set.filter(status=2).aggregate(total=Sum('count'))[
            "total"]
        return total_sell_count if total_sell_count else 0

    class Meta:
        model = LineCoupon
        exclude = ["id", ]


class UserBoughtCodesSerializer(serializers.ModelSerializer):
    line_coupons = serializers.SerializerMethodField()
    days_left = serializers.SerializerMethodField()
    formatted_created = serializers.SerializerMethodField()
    formatted_expire_date = serializers.SerializerMethodField()
    total_sell_price = serializers.SerializerMethodField()
    total_sell_count = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    def validate(self, attrs):
        print(self.instance)
    def get_user(self, obj):
        return f'{obj.user_first_name} {obj.user_last_name}'

    def get_status(self, obj):
        if get_boolean(obj.status):
            return 'پرداخت شده'
        return "پرداخت نشده"

    def get_formatted_created(self, obj):
        datetime_field = datetime.fromgregorian(datetime=obj.created)
        return datetime_field.strftime("%Y/%m/%d %H:%M:%S")

    def get_formatted_expire_date(self, obj):
        datetime_field = datetime.fromgregorian(datetime=obj.expire_date)
        return datetime_field.strftime("%Y/%m/%d %H:%M:%S")

    def get_line_coupons(self, obj: Coupon):
        user_id = self.context.get("user_id")
        line_coupons = obj.linecoupon_set.filter(closedbasketdetail__closedbasket__status=3).distinct("slug")
        serializer = LineCouponWithCodesSerializer(instance=line_coupons, many=True, context={"user_id": user_id})
        return serializer.data

    def get_days_left(self, obj):
        time_now = timezone.now().date()
        if obj.days_left > time_now:
            return (obj.days_left - timezone.now().date()).days
        else:
            return -1

    def get_total_sell_price(self, obj: Coupon):
        total_sell_price = obj.linecoupon_set.filter(closedbasketdetail__closedbasket__status=3).aggregate(
            total_price=Sum("closedbasketdetail__total_price_with_offer"))["total_price"]
        return total_sell_price if total_sell_price else 0

    def get_total_sell_count(self, obj: Coupon):
        total_sell_count = obj.linecoupon_set.filter(closedbasketdetail__closedbasket__status=3).aggregate(
            total_count=Sum("closedbasketdetail__count"))["total_count"]
        return total_sell_count if total_sell_count else 0

    class Meta:
        model = Coupon
        exclude = ["id", "business", "description", "terms_of_use", "coupon_rate", "rate_count", "category"]


class WalletSerializer(serializers.ModelSerializer):
    # sold_coupons = serializers.SerializerMethodField()
    total_sell = serializers.SerializerMethodField()
    total_withdraw = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()

    # def get_sold_coupons(self, obj: Business):
    #     user_id = self.context.get("user_id")
    #     sold_coupons = (
    #         obj.coupon_set.filter(linecoupon__closedbasketdetail__closedbasket__status=3).distinct("id").annotate(
    #             days_left=F('expire_date')
    #         ))
    #     serializer = UserBoughtCodesSerializer(instance=sold_coupons, many=True, context={"user_id": user_id})
    #
    #     return serializer.data

    def get_total_sell(self, obj: Business):
        if self.context["superuser"]:
            deposit_amount = \
                Transaction.objects.filter(type=1, status=2).aggregate(sum=Sum("amount"))["sum"]
        else:
            deposit_amount = \
                Transaction.objects.filter(user_id=obj.admin_id, type=1, status=2).aggregate(sum=Sum("amount"))["sum"]
        return deposit_amount if deposit_amount else 0

    def get_total_withdraw(self, obj: Business):
        if self.context["superuser"]:
            withdraw_amount = \
                Transaction.objects.filter(type=2, status=2).aggregate(sum=Sum("amount"))["sum"]
        else:
            withdraw_amount = \
                Transaction.objects.filter(user_id=obj.admin_id, type=2, status=2).aggregate(sum=Sum("amount"))["sum"]
        return withdraw_amount if withdraw_amount else 0

    def get_balance(self, obj: Business):
        return self.get_total_sell(obj) - self.get_total_withdraw(obj)

    class Meta:
        model = Business
        exclude = ['id', ]
