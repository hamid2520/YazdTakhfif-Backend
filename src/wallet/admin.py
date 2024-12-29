from django.contrib import admin
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered
from .models import Transaction
from unfold.admin import ModelAdmin


@admin.register(Transaction)
class TransactionAdmin(ModelAdmin):
    list_display = ["user", "type", "amount", "status", "customer"]
    list_editable = ["type", "status"]
    search_fields = ["user__phone", "user__username", "customer"]
    list_filter = ["datetime", ]
