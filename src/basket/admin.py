from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import Form

from .models import Basket, BasketDetail, ClosedBasket, ClosedBasketDetail, ProductValidationCode


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at", "total_price", "total_offer_percent", "total_price_with_offer"]
    list_filter = ["created_at"]
    search_fields = ["user__username", "user__email", "total_price", "total_price_with_offer"]
    autocomplete_fields = ["user", "product"]
    readonly_fields = ["slug", "count", "total_price", "total_offer_percent", "total_price_with_offer",
                       "payment_datetime"]


@admin.register(BasketDetail)
class BasketDetailAdmin(admin.ModelAdmin):
    list_display = ["line_coupon", "count", "total_price", "total_price_with_offer", ]
    list_editable = ["count", ]
    search_fields = ["line_coupon__title", "line_coupon__coupon__title"]
    autocomplete_fields = ["line_coupon", ]
    readonly_fields = ["slug", "payment_price", "payment_offer_percent", "payment_price_with_offer", "total_price",
                       "total_price_with_offer", ]


@admin.register(ClosedBasket)
class ClosedBasketAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at", "payment_datetime", "status", "total_price", "total_offer_percent",
                    "total_price_with_offer"]
    list_editable = ["status", ]
    list_filter = ["created_at", "payment_datetime", "status"]
    search_fields = ["user__username", "user__email", "total_price", "total_price_with_offer"]
    autocomplete_fields = ["user", "product"]
    readonly_fields = ["slug", "count", "payment_datetime", "total_price", "total_offer_percent",
                       "total_price_with_offer", "status"]


@admin.register(ClosedBasketDetail)
class ClosedBasketDetailAdmin(admin.ModelAdmin):
    list_display = ["line_coupon", "status", "count", "total_price", "total_price_with_offer", ]
    list_editable = ["count", "status"]
    list_filter = ["status", ]
    search_fields = ["line_coupon__title", "line_coupon__coupon__title"]
    autocomplete_fields = ["line_coupon", ]
    readonly_fields = ["slug", "payment_price", "payment_offer_percent", "payment_price_with_offer", "total_price",
                       "total_price_with_offer", ]


#
@admin.register(ProductValidationCode)
class ProductValidationCodeAdmin(admin.ModelAdmin):
    list_display = ["product", "code", "used", "closed_basket"]
    list_editable = ["used", "closed_basket"]
    list_filter = ["used", ]
    search_fields = ["product__title", "product__coupon__title", "code"]
    autocomplete_fields = ["product", "closed_basket"]
    readonly_fields = ["code", ]
