from django.contrib import admin

from src.payment.models import Payment


class PaymentAdmin(admin.ModelAdmin):
    list_display = ["__str__", "basket", "user", "total_price", "total_price_with_offer"]
    list_filter = ["basket", "user"]


admin.site.register(Payment, PaymentAdmin)
