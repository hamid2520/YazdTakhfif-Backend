from rest_framework import serializers
from jdatetime import datetime
from django.db.models import Sum

from src.basket.models import ClosedBasketDetail, ClosedBasket
from src.business.models import Business
from src.coupon.models import Comment, LineCoupon
from src.coupon.serializers import CommentSerializer
from src.users.models import User


class UserShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "profile_picture", "address"]


class SoldCouponsSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    payment_datetime = serializers.SerializerMethodField()
    line_coupon = serializers.SlugRelatedField(slug_field="title", read_only=True)

    def get_payment_datetime(self, obj: ClosedBasketDetail):
        return datetime.fromgregorian(datetime=obj.closedbasket_set.first().payment_datetime).strftime("%Y/%m/%d")

    def get_status(self, obj):
        status = ["در انتظار تایید", "موفق", "ناموفق"]
        return status[obj.status - 1]

    class Meta:
        model = ClosedBasketDetail
        exclude = ["id", "payment_price", "payment_offer_percent", "payment_price_with_offer", "total_price"]


class SellerDashboardSerializer(serializers.ModelSerializer):
    admin = UserShowSerializer(read_only=True)
    total_sell_price = serializers.SerializerMethodField()
    total_active_coupons = serializers.SerializerMethodField()
    verified_comments = serializers.SerializerMethodField()
    recently_sold_coupons = serializers.SerializerMethodField()

    def get_total_sell_price(self, obj: Business):
        user = obj.admin
        total_sell_price = \
            ClosedBasketDetail.objects.filter(line_coupon__coupon__business_id=obj.id, status=2).aggregate(
                total=Sum('total_price_with_offer'))['total']
        return total_sell_price
    def get_total_active_coupons(self,obj: Business):
        return obj.coupon_set.count()

    def get_verified_comments(self, obj):
        comments = Comment.objects.filter(coupon__business_id=obj.id, verified=True).order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return serializer.data

    def get_recently_sold_coupons(self, obj):
        sold_coupons = ClosedBasketDetail.objects.filter(line_coupon__coupon__business_id=obj.id).order_by(
            'closedbasket__payment_datetime')
        serializer = SoldCouponsSerializer(instance=sold_coupons, many=True)
        return serializer.data

    class Meta:
        model = Business
        exclude = ["id", ]
