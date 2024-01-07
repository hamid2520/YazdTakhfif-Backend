import jdatetime
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from src.basket.models import Basket, ClosedBasket, ClosedBasketDetail
from .models import Payment, get_instance_values


class PaymentSerializer(serializers.ModelSerializer):
    basket_id = serializers.SlugField()
    formatted_created_at = serializers.SerializerMethodField()

    def get_formatted_created_at(self, obj):
        datetime_field = jdatetime.datetime.fromgregorian(datetime=obj.created_at)
        return datetime_field.strftime("%Y/%m/%d %H:%M:%S")

    def validate_basket_id(self, value):
        basket = Basket.objects.filter(slug=value)
        if basket.exists():
            basket = basket.first()
            errors = []
            for product in basket.product.all():
                if (product.count + product.line_coupon.sell_count) > product.line_coupon.count:
                    errors.append(f"{product.line_coupon.title}`s count is more than available count!")
            if errors:
                raise ValidationError(errors)
            return value
        raise ValidationError("Basket does not exists!")

    def validate(self, attrs):
        return super().validate(attrs)

    def save(self, **kwargs):
        if not self.instance:
            data = self.validated_data
            basket = Basket.objects.get(slug=data.get("basket_id"))
            # create closed basket
            kwargs = get_instance_values(basket)
            closed_basket = ClosedBasket.objects.create(**kwargs)
            for product in basket.product.all():
                kwargs = get_instance_values(product)
                closed_basket_product = ClosedBasketDetail.objects.create(**kwargs)
                closed_basket_product.save()
                closed_basket.product.add(closed_basket_product)
            closed_basket.save()
            # delete basket and it's products
            basket.delete()
            # value field basket and create model payment
            del self.validated_data["basket_id"]
            self.validated_data["basket"] = closed_basket
            self.instance = self.create(self.validated_data)
        return self.instance

    class Meta:
        model = Payment
        fields = ["slug", "user", "basket", "basket_id", "total_price", "total_price_with_offer", "created_at",
                  "formatted_created_at"]
        read_only_fields = ["slug", "basket", "created_at", "total_price", "total_price_with_offer"]


class GiftSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=64)
    last_name = serializers.CharField(max_length=64)
    email = serializers.EmailField(max_length=256)
    phone = serializers.CharField(max_length=11)
