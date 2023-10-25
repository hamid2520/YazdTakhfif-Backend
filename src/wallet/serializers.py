from rest_framework import serializers

from .models import *
from src.users.serializers import UserSerializer


class AccountSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    type = models.SmallIntegerField(choices=Account.TYPE_CHOICES)

    class Meta:
        model = Account
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
        }


class TransactionSerializer(serializers.ModelSerializer):
    to_account = AccountSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
        }


class SetBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = 'balance'
        extra_kwargs = {
            'id': {'read_only': True},
        }

    def collect(queryset):
        balance = 0
        for x in queryset:
            balance = balance + x.balance

        return balance
