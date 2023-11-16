from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import BasketViewSet, BasketDetailViewSet, ClosedBasketAPIView, PaidClosedBasketListAPIView, \
    PaidClosedBasketDetailListAPIView, ClosedBasketDetailValidatorAPIView, GetQRCode, VerifyQRCode, UserBasketProductCount, CurrentUserBasketDetail

router = SimpleRouter()
router.register(prefix="baskets", viewset=BasketViewSet, basename="basket", )
router.register(prefix="basket-details", viewset=BasketDetailViewSet, basename="basket_detail", )
urlpatterns = [
                  path("closed-baskets/<slug:slug>/", ClosedBasketAPIView.as_view(), name="closed_basket_detail"),
                  path('user-basket-product-count/', UserBasketProductCount.as_view(), name='user_basket_product_count'),
                  path("closed-baskets/", ClosedBasketAPIView.as_view(), name="closed_basket_list"),
                  path("paid-closed-baskets/", PaidClosedBasketListAPIView.as_view(), name="paid_closed_basket_list"),
                  path("paid-closed-basket-details/<slug:slug>/", PaidClosedBasketDetailListAPIView.as_view(),
                       name="paid_closed_basket_details_list"),
                  path("paid-closed-basket-detail-validator/<slug:slug>/", ClosedBasketDetailValidatorAPIView.as_view(),
                       name="paid_closed_basket_detail_validator"),
                  path("get-qrcode/<slug:slug>/", GetQRCode.as_view(),
                       name="get_qrcode"),
                  path("verify-qrcode/<slug>/", VerifyQRCode.as_view(),
                       name="verify_qrcode"),
                  path('user-bought-coupon/', CurrentUserBasketDetail.as_view(), name='user_bought_coupon')
              ] + router.urls