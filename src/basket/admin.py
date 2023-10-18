from django.contrib import admin

from .models import Basket, BasketDetail, ClosedBasket, ClosedBasketDetail, ProductValidationCode


class BasketAdmin(admin.ModelAdmin):
    list_display = ["__str__", "created_at", "is_paid", "status", "payment_datetime", ]
    list_editable = ["status", "is_paid", ]
    list_filter = ["created_at", "is_paid", "payment_datetime", ]
    readonly_fields = ["count", "total_price", "total_offer_percent", "total_price_with_offer", "payment_datetime", ]


class BasketDetailAdmin(admin.ModelAdmin):
    list_display = ["__str__", "line_coupon", "count", "payment_price", "payment_offer_percent", "total_price", ]
    list_editable = ["count", ]
    readonly_fields = ["payment_price", "payment_offer_percent", "payment_price_with_offer", "total_price",
                       "total_price_with_offer", ]


class ClosedBasketAdmin(BasketAdmin):
    pass


class ClosedBasketDetailAdmin(admin.ModelAdmin):
    list_display = ["__str__", "line_coupon", "status", "count", "payment_price", "payment_offer_percent",
                    "total_price", ]
    list_editable = ["status", "count", ]
    readonly_fields = ["payment_price", "payment_offer_percent", "payment_price_with_offer", "total_price",
                       "total_price_with_offer", ]


class ProductValidationCodeAdmin(admin.ModelAdmin):
    list_display = ["__str__", "code", "used"]
    list_editable = ["used"]
    readonly_fields = ["code"]


admin.site.register(Basket, BasketAdmin)
admin.site.register(BasketDetail, BasketDetailAdmin)
admin.site.register(ClosedBasket, ClosedBasketAdmin)
admin.site.register(ClosedBasketDetail, ClosedBasketDetailAdmin)
admin.site.register(ProductValidationCode,ProductValidationCodeAdmin)
