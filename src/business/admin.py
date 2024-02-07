from django.contrib import admin
from django.db.models import Sum

from src.business.models import Business
from src.wallet.models import Transaction


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ["title", "admin", "deposit", "withdraw", "balance"]
    search_fields = ["title", "admin__username"]
    autocomplete_fields = ["admin"]
    readonly_fields = ["slug", "deposit", "withdraw", "balance"]

    def deposit(self, obj):
        if obj.admin.is_superuser:
            deposit = Transaction.objects.filter(type=1, status=2).aggregate(Sum("amount"))[
                "amount__sum"]
        else:
            deposit = Transaction.objects.filter(user_id=obj.admin_id, type=1, status=2).aggregate(Sum("amount"))[
                "amount__sum"]
        return deposit if deposit else 0

    deposit.short_description = "واریز"

    def withdraw(self, obj):
        if obj.admin.is_superuser:
            withdraw = Transaction.objects.filter(type=2, status=2).aggregate(Sum("amount"))[
                "amount__sum"]
        else:
            withdraw = Transaction.objects.filter(user_id=obj.admin_id, type=2, status=2).aggregate(Sum("amount"))[
                "amount__sum"]
        return withdraw if withdraw else 0

    withdraw.short_description = "برداشت"

    def balance(self, obj):
        return self.deposit(obj) - self.withdraw(obj)

    balance.short_description = "موجودی"
