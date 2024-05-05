from pyexpat import model
from rest_framework import serializers

from src.users.models import User
from src.common.serializers import ThumbnailerJSONSerializer


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(allow_blank=True, write_only=True)

    def update(self, instance, validated_data):
        temp_pass = instance.password
        new_instance = super(UserSerializer, self).update(instance, validated_data)
        if 'password' in validated_data and validated_data.get('password', ''):
            new_instance.set_password(validated_data['password'])
        else:
            new_instance.password = temp_pass
        new_instance.save()
        return new_instance

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'address',
            'phone',
            'password'
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


class AdminUserSerializer(UserSerializer):
    has_business = serializers.SerializerMethodField()

    def get_has_business(self, obj):
        from src.business.models import Business
        return Business.objects.filter(admin__username=obj.username).count() > 0

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'is_staff',
            'email',
            'address',
            'phone',
            'has_business',
            'password'
        )
        read_only_fields = ('username', 'is_staff', )
