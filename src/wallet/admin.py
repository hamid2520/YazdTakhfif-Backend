from django.contrib import admin
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from . import models


class TransactionAdmin(admin.ModelAdmin):
    list_filter = ("to_account__owner",)


class AccountAdmin(admin.ModelAdmin):
    actions = ['withdraw']

    def withdraw(self, request, queryset):
        azeto = models.Account.objects.get(id=models.Account.ACCOUNT_AZETO_COMMISSION_ID)
        azeto_balance = azeto.balance
        for item in queryset:
            balance = item.balance
            new_balance = azeto_balance - balance
            azeto.balance = new_balance
            azeto.save()
            item.balance = 0
            item.save()
            transaction = models.Transaction.objects.create(from_account=item, to_account=azeto,
                                                            type=models.Transaction.TYPE_WITHDRAW_COMMISSION,
                                                            amount=balance)
            models.Turnover.objects.create(transaction=transaction, account=item, balance=balance)
            models.Turnover.objects.create(transaction=transaction, account=azeto, balance=balance)


try:
    admin.site.register(models.Transaction, TransactionAdmin)
    admin.site.register(models.Account, AccountAdmin)

    # admin.site.register(models.Exercise, ExerciseAdmin)
except AlreadyRegistered:
    pass

app_models = apps.get_app_config('wallet').get_models()
for model in app_models:
    try:
        if model not in [models.Transaction, models.Account]:
            admin.site.register(model)
    except AlreadyRegistered:
        pass
