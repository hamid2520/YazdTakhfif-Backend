from rest_framework.routers import SimpleRouter
from django.urls import path
from .views import OfferViewSet, html_to_pdf

router = SimpleRouter()
router.register(prefix="offers", viewset=OfferViewSet, basename="offers")

urlpatterns = [
                  path("pdf/<slug:slug>/", html_to_pdf)
              ] + router.urls
