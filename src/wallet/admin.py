from django.contrib import admin
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["user", "type", "amount", "status", "customer"]
    list_editable = ["type", "status"]
