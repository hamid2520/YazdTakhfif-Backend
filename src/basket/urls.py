from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import BasketViewSet

router = SimpleRouter()
router.register(prefix="baskets", viewset=BasketViewSet, basename="basket")
urlpatterns = router.urls
