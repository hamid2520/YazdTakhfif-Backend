from django.contrib import admin

from src.payment.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["user", "basket", "total_price", "total_price_with_offer", "created_at", ]
    list_filter = ["created_at", ]
    search_fields = ["user__username", "basket__product__line_coupon__title",
                     "basket__product__line_coupon__coupon__title"]
    autocomplete_fields = ["user", "basket"]
    readonly_fields = ["created_at"]
