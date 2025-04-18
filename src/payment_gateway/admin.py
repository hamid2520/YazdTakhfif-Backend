from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Gateway, OnlinePayment


@admin.register(Gateway)
class GatewayAdmin(ModelAdmin):
    list_display = ["name", "gateway", "active", ]
    list_editable = ["active", ]
    list_filter = ["active", "gateway"]
    search_fields = ["name", "gateway"]


@admin.register(OnlinePayment)
class OnlinePaymentAdmin(ModelAdmin):
    list_display = ["user", "status", "gateway", "payment", "paid_at"]
    list_filter = ["status", "gateway", "paid_at", ]
    search_fields = ["user__username", "user__phone", "payment__user__username", "token", "ref_id", "user__first_name", "user__last_name"]
    autocomplete_fields = ["user", "gateway", "payment"]
    readonly_fields = ["user", "status", "token", "gateway", "extra_data", "response", "ref_id", "payment", "paid_at", ]
