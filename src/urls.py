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
                  path('business/', include('src.business.urls')),
                  path('coupon/', include('src.coupon.urls')),
                  path('basket/', include('src.basket.urls')),
                  path('payment/', include('src.payment.urls')),
                  path('payment-gateway/', include('src.payment_gateway.urls')),
                  path('offer/', include('src.offer.urls')),
                  path('advertise/', include('src.advertise.urls')),
                  path('search/', include('src.search_engine.urls')),
                  # admin panel
                  path('admin/', admin.site.urls),
                  # url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
                  # summernote editor
                  path('summernote/', include('django_summernote.urls')),
                  # api
                  path('api/v1/', include(router.urls)),
                  url(r'^api/v1/password_reset/',
                      include('django_rest_passwordreset.urls', namespace='password_reset')),
                  # auth
                  path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                  path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
                  path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
                  # social login
                  url('', include('social_django.urls', namespace='social')),
                  # swagger docs
                  url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0),
                      name='schema-json'),
                  url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
                  url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
                  url(r'^health/', include('health_check.urls')),
                  # the 'api-root' from django rest-frameworks default router
                  re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

