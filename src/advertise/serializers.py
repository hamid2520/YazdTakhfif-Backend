from rest_framework.serializers import ModelSerializer

from .models import Advertise


class AdvertiseSerializer(ModelSerializer):
    class Meta:
        model = Advertise
        fields = ["file", "link", ]
