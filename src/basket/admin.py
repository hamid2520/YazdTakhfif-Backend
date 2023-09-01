from django.contrib import admin
from django.db.models import Sum

from .models import Basket, BasketDetail


class BasketAdmin(admin.ModelAdmin):
    list_display = ["__str__", "created_at", "is_paid", "payment_datetime", ]
    list_editable = ["is_paid", ]
    list_filter = ["created_at", "is_paid", "payment_datetime", ]
    readonly_fields = ["count", "total_price", "total_offer_percent", "total_price_with_offer", "payment_datetime", ]

    def save_model(self, request, obj, form, change):
        form.save()
        count = obj.product.all().aggregate(Sum("count"))
        obj.count = count.get("count__sum")
        obj.save()


class BasketDetailAdmin(admin.ModelAdmin):
    list_display = ["__str__", "line_coupon", "count", "payment_price", "payment_offer_percent", "final_price", ]
    list_editable = ["count", ]
    readonly_fields = ["payment_price", "payment_offer_percent", "payment_price_with_offer", "final_price",
                       "final_price_with_offer", ]


admin.site.register(Basket, BasketAdmin)
admin.site.register(BasketDetail, BasketDetailAdmin)
