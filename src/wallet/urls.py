from django.urls import path
from .views import WalletView, WalletCouponsView

urlpatterns = [
    path('', WalletView.as_view(), name="wallet_view"),
    path('sold-coupons/', WalletCouponsView.as_view(), name="sold_coupons"),
]
