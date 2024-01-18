from rest_framework.routers import SimpleRouter
from django.urls import path

from .views import AdvertiseViewSet, AdvertiseSliderApiView, NewsLetterViewSet

router = SimpleRouter()
router.register(prefix="advertises", viewset=AdvertiseViewSet, basename="advertise")
router.register(prefix="news", viewset=NewsLetterViewSet, basename="news")

urlpatterns = [
    path("slider/", AdvertiseSliderApiView.as_view(), name="list_slider_api"),
] + router.urls
