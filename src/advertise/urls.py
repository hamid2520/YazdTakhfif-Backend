from rest_framework.routers import SimpleRouter

from .views import AdvertiseViewSet

router = SimpleRouter()
router.register(prefix="advertises", viewset=AdvertiseViewSet, basename="advertise")

urlpatterns = router.urls
