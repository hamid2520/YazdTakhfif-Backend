from rest_framework.routers import SimpleRouter

from .views import PaymentViewSet

router = SimpleRouter()
router.register("payments", PaymentViewSet, "payment")

urlpatterns = router.urls
