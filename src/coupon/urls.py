from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import CategoryViewSet, CouponViewSet, LineCouponViewSet

router = SimpleRouter()
router.register(prefix="categories", viewset=CategoryViewSet, basename="category")
router.register(prefix="coupons", viewset=CouponViewSet, basename="coupon")
router.register("line-coupons", LineCouponViewSet, "line_coupon")
urlpatterns = [
                  path("line-coupons/list/<slug:slug>/", LineCouponViewSet.as_view({"get": "list"}),
                       name="line_coupon_list"),
              ] + router.urls
