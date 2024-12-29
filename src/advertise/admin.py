from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Advertise, NewsLetter


@admin.register(Advertise)
class AdvertiseAdmin(ModelAdmin):
    list_display = ["title", "is_slider", "link"]
    list_editable = ["is_slider", "link"]
    list_filter = ["is_slider", ]
    search_fields = ["title", "link"]


@admin.register(NewsLetter)
class NewsLetterAdmin(ModelAdmin):
    list_display = ["email", "user"]
    search_fields = ["email", "user"]
