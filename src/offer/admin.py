from django.contrib import admin

from src.offer.models import Offer


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ["offer_code", "percent", "start_date", "expire_date", "maximum_offer_price", ]
    list_filter = ["start_date", "expire_date"]
    search_fields = ["offer_code", "limited_businesses__title"]
    autocomplete_fields = ["limited_businesses", ]

