from rest_framework.routers import SimpleRouter
from django.urls import path
from .views import PaymentViewSet,ValidateGiftAPIView

router = SimpleRouter()
router.register("payments", PaymentViewSet, "payment")

urlpatterns = [
    path("validate-gift/", ValidateGiftAPIView.as_view(), name="validate_gift")
              ] + router.urls
