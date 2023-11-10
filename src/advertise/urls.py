from rest_framework.routers import SimpleRouter
from django.urls import path

from .views import AdvertiseViewSet, AdvertiseSliderApiView

router = SimpleRouter()
router.register(prefix="advertises", viewset=AdvertiseViewSet, basename="advertise")

urlpatterns = [
    path("slider/", AdvertiseSliderApiView.as_view(), name="list_slider_api"),
] + router.urls
