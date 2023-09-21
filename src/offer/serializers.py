from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Offer
from ..business.models import Business


class OfferSerializer(serializers.ModelSerializer):
    def validate_limited_businesses(self, value):
        user = self.context.get("request").user
        if not user.is_superuser:
            business = Business.objects.filter(admin__id=user.id)
            if not business.exists():
                raise ValidationError("You have no business!")
            business = business.first()
            value = [business.id, ]
        return value

    class Meta:
        model = Offer
        fields = ["offer_code", "percent", "start_date", "expire_date", "limited_businesses", "maximum_offer_price"]
