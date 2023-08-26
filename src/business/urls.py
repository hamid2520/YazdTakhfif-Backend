from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import BusinessViewSet

router = SimpleRouter()
router.register(prefix="", viewset=BusinessViewSet, basename="business")
urlpatterns = router.urls
