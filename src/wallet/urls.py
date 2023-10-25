from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()


router.register('transaction', views.TransactionViewSet,
                basename='transaction')
router.register('account', views.AccountViewSet, basename='account')

urlpatterns = [
    path('', include(router.urls)),
    path('cart/', views.SetCommissionTurnover.as_view(), name='cart'),
    # path('charge/', views.AccountCharge.as_view(), name='charge'),
    path('settlement/',views.RequestSettlementView.as_view(), name='settlement'),
]
