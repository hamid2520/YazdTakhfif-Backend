from django.contrib import admin

from .models import Gateway, OnlinePayment


class OnlinePaymentAdmin(admin.ModelAdmin):
    list_display = ["token", "status", "payment"]
    list_editable = ["status", ]


admin.site.register(Gateway)
admin.site.register(OnlinePayment,OnlinePaymentAdmin)
