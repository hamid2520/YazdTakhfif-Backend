import jdatetime
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Offer
from ..basket.models import Basket
from ..business.models import Business


class OfferSerializer(serializers.ModelSerializer):
    limited_businesses = serializers.SlugRelatedField(slug_field="slug", queryset=Business.objects.all(), many=True)
    formatted_start_date = serializers.SerializerMethodField()
    formatted_expire_date = serializers.SerializerMethodField()

    def get_formatted_start_date(self, obj):
        datetime_field = jdatetime.datetime.fromgregorian(datetime=obj.start_date)
        return datetime_field.strftime("%Y/%m/%d %H:%M:%S")

    def get_formatted_expire_date(self, obj):
        datetime_field = jdatetime.datetime.fromgregorian(datetime=obj.expire_date)
        return datetime_field.strftime("%Y/%m/%d %H:%M:%S")

    def validate_limited_businesses(self, value):
        user = self.context.get("request").user
        if not user.is_superuser:
            for business in value:
                if business.admin.id != user.id:
                    raise ValidationError("You must choose only your own businesses!")
        return value

    class Meta:
        model = Offer
        fields = ["offer_code", "percent", "start_date", "expire_date", "limited_businesses", "maximum_offer_price",
                  "formatted_start_date",
                  "formatted_expire_date"]


class OfferValidatorSerializer(serializers.Serializer):
    offer_code = serializers.CharField(max_length=16)
    apply_to_basket = serializers.BooleanField(default=False)

    def validate_offer_code(self, value):
        offer = Offer.objects.filter(offer_code=value)
        if offer.exists():
            return value
        raise ValidationError("Offer code is not valid!")
