from django.apps import AppConfig


class CouponConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.coupon'
    verbose_name = "مدیریت کوپن"

    def ready(self):
        from . import signals
