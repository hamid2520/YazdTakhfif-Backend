from django.apps import AppConfig


class PaymentGatewayConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.payment_gateway'
