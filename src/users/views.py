from rest_framework.request import Request
from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from src.users.models import User
from src.users.permissions import IsUserOrReadOnly
from src.users.serializers import CreateUserSerializer, UserSerializer, SignInSerializer, LoginSerializer
from rest_framework import pagination


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
        try:
            return Response(UserSerializer(self.request.user, context={'request': self.request}).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Wrong auth token' + str(e)}, status=status.HTTP_400_BAD_REQUEST)



class UserSignInView(APIView):
    def post(self, request : Request):
        serializer = SignInSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            if phone :
               user, created = User.objects.get_or_create(phone=phone, username=phone)
               user.sms_code ='12345'
               user.save()
               return Response(status=status.HTTP_200_OK)
                
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)




class UserLogingView(APIView):
    def post(self,request : Request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            sms_code = serializer.validated_data['sms_code']
            user = User.objects.filter(phone=phone, sms_code=sms_code).first()

            if user :
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)},
                    status=status.HTTP_202_ACCEPTED
                    )

            else :
                return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_400_BAD_REQUEST)


'''
{
"phone":"09162151698",
"sms_code":"12345"
}
'''