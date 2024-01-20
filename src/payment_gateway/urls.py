from django.urls import path
from azbankgateways.urls import az_bank_gateways_urls

from .views import go_to_gateway_view_v2, callback_gateway_view_v2, PaymentResultAPIView, PaymentBasketAPIView, \
    BasketCountValidationAPIView

urlpatterns = [
    path('', az_bank_gateways_urls()),
    path('go-to-gateway/<slug:slug>/', go_to_gateway_view_v2, name="go-to-gateway-v2"),
    path('callback-gateway/<str:token>/', callback_gateway_view_v2, name="callback-gateway-v2"),
    path('payment-result/<int:payment_status>/', PaymentResultAPIView.as_view(), name="payment_result"),
    path('payment-basket/', PaymentBasketAPIView.as_view(), name="payment_basket"),
    path('final-count-validation/<slug:basket_slug>/', BasketCountValidationAPIView.as_view(),
         name="final_count_validation"),
]
