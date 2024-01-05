from django.urls import path
from azbankgateways.urls import az_bank_gateways_urls

from .views import go_to_gateway_view_v2, callback_gateway_view_v2, payment_result, BasketCountValidationAPIView

urlpatterns = [
    path('', az_bank_gateways_urls()),
    path('go-to-gateway/<slug:slug>/', go_to_gateway_view_v2, name="go-to-gateway-v2"),
    path('callback-gateway/<str:token>/', callback_gateway_view_v2, name="callback-gateway-v2"),
    path('payment-result/<str:token>/<int:status>/', payment_result, name="payment_result"),
    path('final-count-validation/<slug:basket_slug>/', BasketCountValidationAPIView.as_view(),
         name="final_count_validation"),
]
