from django.urls import path
from rest_framework.routers import SimpleRouter
from src.users.views import UserViewSet, UserSignInView, UserLogingView

users_router = SimpleRouter()

users_router.register(r'users', UserViewSet)

urlpatterns = [
    path('sms/', UserSignInView.as_view()),
    path('login-sms/', UserLogingView.as_view()),
] + users_router.urls
