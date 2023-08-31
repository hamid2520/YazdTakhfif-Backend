from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import BasketViewSet,BasketDetailViewSet

router = SimpleRouter()
router.register(prefix="baskets", viewset=BasketViewSet, basename="basket",)
router.register(prefix="basket-details", viewset=BasketDetailViewSet, basename="basket_detail",)
urlpatterns = [
                  path("basket-details/list/<slug:slug>/", BasketDetailViewSet.as_view({"get": "list"}),
                       name="basket_detail_list"),
              ] + router.urls
