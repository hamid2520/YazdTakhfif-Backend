from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import BusinessViewSet, DepositViewSet, CorporateViewSet

router = SimpleRouter()
router.register(prefix="", viewset=BusinessViewSet, basename="business")
router.register(r'deposit', DepositViewSet, 'deposit_api')

urlpatterns = [
    path('corporate/', CorporateViewSet.as_view())
] + router.urls
