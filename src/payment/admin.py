from django.contrib import admin
from unfold.admin import ModelAdmin

from src.payment.models import Payment


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ["user", "basket", "total_price", "total_price_with_offer", "created_at", ]
    list_filter = ["created_at", ]
    search_fields = ["user__username", "basket__product__line_coupon__title",
                     "basket__product__line_coupon__coupon__title"]
    autocomplete_fields = ["user", "basket"]
    readonly_fields = ["slug", "created_at", "coupon_titles"]


    def get_queryset(self, request):
        queryset = super().get_queryset(request)
#        queryset = queryset.select_related('basket__product__line_coupon__coupon')
        return queryset

    def coupon_titles(self, obj):
        titles = []
        for product in obj.basket.product.all():
            line_coupon = product.line_coupon
            if line_coupon and line_coupon.coupon:
                titles.append(f"{line_coupon.coupon.title} (لاین کوپن: {line_coupon.title})")
        return ", ".join(titles) if titles else "بدون محصول"

    coupon_titles.short_description = "لیست سفارشات"
