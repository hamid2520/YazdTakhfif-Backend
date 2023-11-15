from django.contrib import admin

from src.business.models import Business


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ["title", "admin"]
    search_fields = ["title", "admin__username"]
    autocomplete_fields = ["admin"]
