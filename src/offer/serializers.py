from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Offer
from ..business.models import Business


class OfferSerializer(serializers.ModelSerializer):
    def validate_limited_businesses(self, value):
        user = self.context.get("request").user
        if not user.is_superuser:
            for business in value:
                if business.admin.id != user.id:
                    raise ValidationError("You must choose only your own businesses!")
        return value

    class Meta:
        model = Offer
        fields = ["offer_code", "percent", "start_date", "expire_date", "limited_businesses", "maximum_offer_price"]
