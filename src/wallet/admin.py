from django.contrib import admin
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered
from . import models


class TransactionAdmin(admin.ModelAdmin):
    list_filter = ("to_account__owner",)


class AccountAdmin(admin.ModelAdmin):
    actions = ['withdraw']

    def withdraw(self, request, queryset):
        yazd_takhfif = models.Account.objects.get(id=models.Account.ACCOUNT_YAZD_TAKHFIF_COMMISSION_ID)
        yazd_takhfif_balance = yazd_takhfif.balance
        for item in queryset:
            balance = item.balance
            new_balance = yazd_takhfif_balance - balance
            yazd_takhfif.balance = new_balance
            yazd_takhfif.save()
            item.balance = 0
            item.save()
            transaction = models.Transaction.objects.create(from_account=item, to_account=yazd_takhfif,
                                                            type=models.Transaction.TYPE_WITHDRAW_COMMISSION,
                                                            amount=balance)
            models.Turnover.objects.create(transaction=transaction, account=item, balance=balance)
            models.Turnover.objects.create(transaction=transaction, account=yazd_takhfif, balance=balance)


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
