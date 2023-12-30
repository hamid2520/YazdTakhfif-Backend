from rest_framework.filters import SearchFilter
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.shortcuts import redirect
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import F
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
# from core.util.mixin import IsAuthenticatedPermission
from . import serializers
from . import models
# from accounting.models import Payment, OnlinePayment, Gateway
import logging
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from rest_framework import status

from .serializers import WalletSerializer, UserBoughtCodesSerializer
# from core.util.extend import RetrieveListViewSet, StandardResultsSetPagination
# from core.util.helper import play_filtering_form
# from .services.services import add_user_commission
from .services import settlement
from azbankgateways import bankfactories, models as bank_models, default_settings as settings
from azbankgateways.apps import AZIranianBankGatewaysConfig
from azbankgateways.exceptions import AZBankGatewaysException

from ..business.models import Business
from .filters import TimeFilter


# class SetCommissionTurnover(APIView):
#     def get(self, request, *args, **kwargs):
#         client = request.user
#         add_user_commission(client, 1000)
#         return Response({"total-price": 1000})
#
#
# class TransactionViewSet(IsAuthenticatedPermission, RetrieveListViewSet):
#     serializer_class = serializers.TransactionSerializer
#     pagination_class = StandardResultsSetPagination
#     queryset = models.Transaction.objects.all()
#
#     def get_queryset(self):
#         user = self.request.user
#         user_acc, created = models.Account.objects.get_or_create(
#             owner=user,
#             type=models.Account.TYPE_COMMISSION,
#         )
#         if self.request.query_params.get('my_withdraw', None) == '1':
#             queryset = models.Transaction.objects.filter(
#                 from_account=user_acc, type=models.Transaction.TYPE_WITHDRAW_COMMISSION)
#             return queryset.all()
#         queryset = models.Transaction.objects.filter(to_account=user_acc)
#         return queryset.all()
#
#     def filter_queryset(self, queryset):
#         queryset = self.get_queryset()
#         queryset = play_filtering_form(queryset, self.request.query_params)
#         return queryset
#
#
# class AccountViewSet(IsAuthenticatedPermission, RetrieveListViewSet):
#     serializer_class = serializers.AccountSerializer
#
#     def get_queryset(self):
#         user = self.request.user
#         result = models.Account.objects.filter(owner=user).all()
#         return result
#
#
# class RequestSettlementView(IsAuthenticatedPermission, APIView):
#     def post(self, request):
#         user = request.user
#         amount = request.data['value']
#         return settlement.add_request_settlement(user, amount)
class WalletView(APIView):
    def get(self, request):
        user_id = request.user.id
        businesses = get_object_or_404(Business, admin_id=user_id)
        serializer = WalletSerializer(instance=businesses, context={'user_id': user_id})
        return Response(serializer.data, status=status.HTTP_200_OK)


# class WalletCouponsView(ListAPIView):
    serializer_class = UserBoughtCodesSerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = [SearchFilter, TimeFilter]
    search_fields = '__all__'

#     def get_queryset(self):
#         user_id = self.request.user.id
#         business = get_object_or_404(Business, admin_id=user_id)
#         sold_coupons = (
#             business.coupon_set.filter(linecoupon__closedbasketdetail__closedbasket__status=3).distinct("id").annotate(
#                 days_left=F('expire_date')
#             ))
#         serializer = UserBoughtCodesSerializer(instance=sold_coupons, many=True, context={"user_id": user_id})
#         return Response(serializer.data, status=status.HTTP_200_OK)
class WalletCouponsView(ListAPIView):
    serializer_class = UserBoughtCodesSerializer
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [IsAuthenticated, ]

    def get_queryset(self):
        user_id = self.request.user.id
        business = get_object_or_404(Business, admin_id=user_id)
        sold_coupons = (
            business.coupon_set.filter(linecoupon__closedbasketdetail__closedbasket__status=3).distinct("id").annotate(
                days_left=F('expire_date')
            ))
        return sold_coupons

    def get_serializer_context(self):
        user_id = self.request.user.id
        context = super().get_serializer_context()
        context['user_id'] = user_id
        return context

    # def get(self, request):
    #     user_id = request.user.id
    #     business = get_object_or_404(Business, admin_id=user_id)
    #     sold_coupons = (
    #         business.coupon_set.filter(linecoupon__closedbasketdetail__closedbasket__status=3).distinct("id").annotate(
    #             days_left=F('expire_date')
    #         ))
    #     serializer = UserBoughtCodesSerializer(instance=sold_coupons, many=True, context={"user_id": user_id})
    #     return Response(serializer.data, status=status.HTTP_200_OK)
