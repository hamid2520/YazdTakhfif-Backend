from django.contrib import admin

from src.offer.models import Offer


class OfferAdmin(admin.ModelAdmin):
    list_display = ["offer_code", "percent", "start_date", "expire_date", "maximum_offer_price"]
    list_filter = ["start_date", "expire_date"]


admin.site.register(Offer, OfferAdmin)
