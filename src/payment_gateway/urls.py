
from django.urls import path
from azbankgateways.urls import az_bank_gateways_urls

from .views import go_to_gateway_view_v2, callback_gateway_view_v2,payment_result

urlpatterns = [
    path('', az_bank_gateways_urls()),
    path('go-to-gateway/<str:token>/', go_to_gateway_view_v2, name="go-to-gateway-v2"),
    path('callback-gateway/<str:token>/', callback_gateway_view_v2, name="callback-gateway-v2"),
    path('payment-result/<str:token>/<int:status>/', payment_result, name="payment_result"),
]
