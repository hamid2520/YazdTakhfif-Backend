from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.urls import path, re_path, include, reverse_lazy

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView, )

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from src.files.urls import files_router
from src.users.urls import users_router

schema_view = get_schema_view(
    openapi.Info(title="Pastebin API", default_version='v1'),
    public=True,
)

router = DefaultRouter()

router.registry.extend(users_router.registry)
router.registry.extend(files_router.registry)

urlpatterns = [
                  # site urls
                  path('api/business/', include('src.business.urls')),
                  path('api/coupon/', include('src.coupon.urls')),
                  path('api/basket/', include('src.basket.urls')),
                  path('api/payment/', include('src.payment.urls')),
                  path('api/payment-gateway/', include('src.payment_gateway.urls')),
                  path('api/offer/', include('src.offer.urls')),
                  path('api/advertise/', include('src.advertise.urls')),
                  path('api/search/', include('src.search_engine.urls')),
                  path('api/seller-dashboard/', include('src.seller_dashboard.urls')),
                  path('api/wallet/', include('src.wallet.urls')),
                  # admin panel
                  path('admin/', admin.site.urls),
                  # url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
                  # summernote editor
                  path('api/summernote/', include('django_summernote.urls')),
                  # api
                  path('api/v1/', include('src.users.urls')),
                  url(r'^api/v1/password_reset/',
                      include('django_rest_passwordreset.urls', namespace='password_reset')),
                  # auth
                  path('api/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                  path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
                  path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
                  # social login
                  url('api/', include('social_django.urls', namespace='social')),
                  # the 'api-root' from django rest-frameworks default router
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

