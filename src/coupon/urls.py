from django.urls import path
from .views import CategoryListApiView, CategoryDetailApiView, CouponListApiView, CouponDetailApiView, \
    LineCouponListApiView

urlpatterns = [
    path("categories/list/", CategoryListApiView.as_view(), name="category_list"),
    path("categories/detail/<slug:slug>/", CategoryDetailApiView.as_view(), name="category_detail"),
    path("coupons/list/", CouponListApiView.as_view(), name="coupon_list"),
    path("coupons/detail/<slug:slug>/", CouponDetailApiView.as_view(), name="coupon_detail"),
    path("line-coupons/list/<slug:slug>/", LineCouponListApiView.as_view(), name="line_coupon_list"),
]
