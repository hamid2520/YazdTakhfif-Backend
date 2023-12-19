from django.urls import path

from .views import SellerDashboardAPIView

urlpatterns = [
    path('', SellerDashboardAPIView.as_view(), name='seller_dashboard')
]
