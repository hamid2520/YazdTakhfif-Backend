from django.contrib import admin

from .models import Gateway, OnlinePayment


@admin.register(Gateway)
class GatewayAdmin(admin.ModelAdmin):
    list_display = ["name", "gateway", "active", ]
    list_editable = ["active", ]
    list_filter = ["active", "gateway"]
    search_fields = ["name", "gateway"]


@admin.register(OnlinePayment)
class OnlinePaymentAdmin(admin.ModelAdmin):
    list_display = ["user", "status", "gateway", "payment", "paid_at", "token", "ref_id"]
    list_filter = ["status", "gateway", "paid_at", ]
    search_fields = ["user__username", "payment__user__username", "token__contains", "ref_id__contains"]
    autocomplete_fields = ["user", "gateway", "payment"]
    readonly_fields = ["user", "status", "token", "gateway", "extra_data", "response", "ref_id", "payment", "paid_at", ]
