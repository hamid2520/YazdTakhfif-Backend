from rest_framework.serializers import ModelSerializer

from .models import Advertise, NewsLetter


class AdvertiseSerializer(ModelSerializer):
    class Meta:
        model = Advertise
        fields = ["file", "link", "is_slider"]


class NewsLetterSerializer(ModelSerializer):
    class Meta:
        model = NewsLetter
        fields = '__all__'

    def get_user(self, obj):
        if self.context['request'].user.is_authenticated:
            return self.context['request'].user
        else:
            return None