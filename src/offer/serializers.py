from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Offer
from ..basket.models import Basket
from ..business.models import Business


class OfferSerializer(serializers.ModelSerializer):
    limited_businesses = serializers.SlugRelatedField(slug_field="slug", queryset=Business.objects.all(), many=True)

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


class OfferValidatorSerializer(serializers.Serializer):
    offer_code = serializers.CharField(max_length=16)
    basket_slug = serializers.SlugField()

    def validate_offer_code(self, value):
        offer = Offer.objects.filter(offer_code=value)
        if offer.exists():
            return value
        raise ValidationError("Offer code is not valid!")

    def validate_basket_slug(self, value):
        basket = Basket.objects.filter(slug=value)
        if basket.exists():
            return value
        raise ValidationError("Basket does not exists!")
