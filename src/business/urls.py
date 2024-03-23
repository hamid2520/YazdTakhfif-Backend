from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import BusinessViewSet, DepositViewSet, CorporateViewSet

router = SimpleRouter()
router.register(r'deposit', DepositViewSet, 'deposit_api')
router.register(prefix="", viewset=BusinessViewSet, basename="business")

urlpatterns = [
    path('corporate/', CorporateViewSet.as_view())
] + router.urls
