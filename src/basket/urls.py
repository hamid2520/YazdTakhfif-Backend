from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import BasketViewSet, BasketDetailViewSet, ClosedBasketAPIView

router = SimpleRouter()
router.register(prefix="baskets", viewset=BasketViewSet, basename="basket", )
router.register(prefix="basket-details", viewset=BasketDetailViewSet, basename="basket_detail", )
urlpatterns = [
                  path("closed-baskets/<slug:slug>/", ClosedBasketAPIView.as_view(), name="closed_basket_detail"),
                  path("closed-baskets/", ClosedBasketAPIView.as_view(), name="closed_basket_list"),
              ] + router.urls