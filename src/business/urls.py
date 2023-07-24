from django.urls import path
from .views import BusinessListApiView, BusinessDetailApiView

urlpatterns = [
    path("list/", BusinessListApiView.as_view(), name="business_list"),
    path("detail/<slug:slug>/", BusinessDetailApiView.as_view(), name="business_detail"),
]
