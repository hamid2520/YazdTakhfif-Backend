from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import CategoryViewSet, CouponViewSet, LineCouponViewSet
from .customer_views import CategoryAPIView, CouponAPIView, LineCouponAPIView

router = SimpleRouter()
router.register(prefix="admin-categories", viewset=CategoryViewSet, basename="category_admin")
router.register(prefix="admin-coupons", viewset=CouponViewSet, basename="coupon_admin")
router.register(prefix="admin-line-coupons", viewset=LineCouponViewSet, basename="line_coupon_admin")
urlpatterns = [
                  path("categories/", CategoryAPIView.as_view(), name="category_list"),
                  path("coupons/detail/<slug:slug>/", CouponAPIView.as_view(), name="coupon_detail"),
                  path("coupons/", CouponAPIView.as_view(), name="coupon_list"),
                  path("line-coupons/<slug:coupon_slug>/", LineCouponAPIView.as_view(), name="line_coupon_list"),
              ] + router.urls
