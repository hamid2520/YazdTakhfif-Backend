from rest_framework import serializers
from rest_framework.settings import api_settings


def raise_not_field_error(msg):
    raise serializers.ValidationError({api_settings.NON_FIELD_ERRORS_KEY: [msg]})
