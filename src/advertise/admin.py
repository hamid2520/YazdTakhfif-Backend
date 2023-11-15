from django.contrib import admin

from .models import Advertise


@admin.register(Advertise)
class AdvertiseAdmin(admin.ModelAdmin):
    list_display = ["title", "is_slider", "link"]
    list_editable = ["is_slider", "link"]
    list_filter = ["is_slider", ]
    search_fields = ["title", "link"]
