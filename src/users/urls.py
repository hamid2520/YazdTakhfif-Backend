from django.urls import path
from rest_framework.routers import SimpleRouter
from src.users.views import UserViewSet, SignInSmsView, UserLoginView, UserBusiness, UserSignUpView, \
    UserSignUpConfirmView

users_router = SimpleRouter()

users_router.register(r'users', UserViewSet)

urlpatterns = [
    path('sms/', SignInSmsView.as_view()),
    path('login-sms/', UserLoginView.as_view()),

    path('sign-up/', UserSignUpView.as_view()),
    path('sign-up/confirm/', UserSignUpConfirmView.as_view()),

    path('user-business/', UserBusiness.as_view()),
] + users_router.urls
