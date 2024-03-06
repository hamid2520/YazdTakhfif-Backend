from pyexpat import model
from rest_framework import serializers

from src.users.models import User
from src.common.serializers import ThumbnailerJSONSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'address',
            'phone'
        )
        read_only_fields = ('username',)


class CreateUserSerializer(serializers.ModelSerializer):
    profile_picture = ThumbnailerJSONSerializer(required=False, allow_null=True, alias_target='src.users')
    tokens = serializers.SerializerMethodField()

    def get_tokens(self, user):
        return user.get_tokens()

    def create(self, validated_data):
        # call create_user on user object. Without this
        # the password will be stored in plain text.
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'password',
            'first_name',
            'last_name',
            'email',
            'tokens',
            'profile_picture',
        )
        read_only_fields = ('tokens',)
        extra_kwargs = {'password': {'write_only': True}}

class SignInSerializer(serializers.Serializer):
    phone = serializers.CharField()


class SignUpSerializer(serializers.Serializer):
    phone = serializers.CharField()
    sms_code = serializers.CharField(allow_null=True)
    password = serializers.CharField(allow_null=True)



class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    sms_code = serializers.CharField()
    signin_type = serializers.CharField()


