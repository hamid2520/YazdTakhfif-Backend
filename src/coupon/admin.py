from django.contrib import admin

from src.coupon.models import Category, Coupon, LineCouponDetail, LineCoupon

admin.site.register(Category)
admin.site.register(Coupon)
admin.site.register(LineCouponDetail)
admin.site.register(LineCoupon)
