from django.contrib.auth.hashers import make_password, check_password
from rest_framework.generics import ListAPIView
from rest_framework.request import Request
from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from src.business.models import Business
from src.business.serializers import BusinessSerializer
from src.users.models import User
from src.users.permissions import IsUserOrReadOnly
from src.users.serializers import CreateUserSerializer, UserSerializer, SignInSerializer, LoginSerializer, \
    SignUpSerializer
from rest_framework import pagination
from django.utils.crypto import get_random_string

from src.users.sms_function import SmsCenter, LOGIN_BODY_ID


class UserViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Creates, Updates and Retrieves - User Accounts
    """

    queryset = User.objects.all()
    serializers = {'default': UserSerializer, 'create': CreateUserSerializer}
    permissions = {'default': (IsUserOrReadOnly,), 'create': (AllowAny,)}
    pagination_class = pagination.LimitOffsetPagination

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers['default'])

    def get_permissions(self):
        self.permission_classes = self.permissions.get(self.action, self.permissions['default'])
        return super().get_permissions()

    @action(detail=False, methods=['get'], url_path='me', url_name='me')
    def get_user_data(self, instance):
        if self.request.user.is_authenticated:
            try:
                return Response(UserSerializer(self.request.user, context={'request': self.request}).data,
                                status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': 'Wrong auth token' + str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class SignInSmsView(APIView):
    def post(self, request: Request):
        serializer = SignInSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            user = User.objects.filter(phone=phone)
            if not user.exists():
                return Response(status=404)
            else:
                user = user.first()
            sms_code = get_random_string(length=4, allowed_chars='1234567890')
            user.sms_code = sms_code
            user.save()
            SmsCenter(sms_template_id=LOGIN_BODY_ID, sms_body=sms_code, receivers=user.phone).send_sms()
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    def post(self, request: Request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            sms_code = serializer.validated_data['sms_code']
            user = User.objects.filter(phone=phone)
            if user.exists():
                if serializer.validated_data['signin_type'] == 'sms' and user.first().sms_code == sms_code:
                    refresh = RefreshToken.for_user(user.first())
                    return Response(status=status.HTTP_200_OK,
                                    data={'refresh': str(refresh), 'access': str(refresh.access_token)})
                elif serializer.validated_data['signin_type'] == 'pass' and check_password(sms_code, user.first().password):
                    refresh = RefreshToken.for_user(user.first())
                    return Response(status=status.HTTP_200_OK,
                                    data={'refresh': str(refresh), 'access': str(refresh.access_token)})
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserSignUpView(APIView):
    def post(self, request: Request):
        serializer = SignInSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            user = User.objects.filter(phone=phone)
            if user.exists():
                user = user.first()
            else:
                user = User.objects.create_user(username=phone, phone=phone, email='')

            sms_code = get_random_string(length=4, allowed_chars='1234567890')
            user.sms_code = sms_code
            user.save()
            SmsCenter(sms_template_id=LOGIN_BODY_ID, sms_body=sms_code, receivers=user.phone).send_sms()
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserSignUpConfirmView(APIView):
    def post(self, request: Request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            user = User.objects.filter(phone=phone)
            if user.exists():
                user = user.first()
                if user.sms_code == serializer.validated_data['sms_code']:
                    user.password = make_password(serializer.validated_data['password'])
                    user.save()
                    refresh = RefreshToken.for_user(user)
                    return Response(status=status.HTTP_200_OK,
                                    data={'refresh': str(refresh),
                                          'access': str(refresh.access_token)})
                else:
                    return Response(status=400)
            else:
                return Response(status=400)

        return Response(status=status.HTTP_400_BAD_REQUEST)
class UserBusiness(ListAPIView):
    serializer_class = BusinessSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Business.objects.all()
        else:
            return Business.objects.filter(admin=self.request.user)

'''
{
"phone":"09162151698",
"sms_code":"12345"
}
'''