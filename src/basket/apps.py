from django.apps import AppConfig


class BasketConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.basket'

    def ready(self):
        from . import signals
