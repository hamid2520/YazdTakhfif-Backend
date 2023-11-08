from rest_framework.routers import SimpleRouter
from django.urls import path
from .views import OfferViewSet

router = SimpleRouter()
router.register(prefix="offers", viewset=OfferViewSet, basename="offers")

urlpatterns = router.urls
