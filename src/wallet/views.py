from rest_framework.filters import SearchFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import redirect
from rest_framework.filters import SearchFilter
from rest_framework.settings import api_settings
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
from ..coupon.models import Coupon


class WalletView(APIView):
    def get(self, request):
        if request.user.is_superuser:
            businesses, created = Business.objects.get_or_create(admin_id=request.user.id, title="یزد تخفیف")
        else:
            businesses = Business.objects.filter(admin_id=request.user.id)
            if not businesses.exists():
                return Response(status=status.HTTP_404_NOT_FOUND)
            businesses = businesses.first()
        serializer = WalletSerializer(instance=businesses,
                                      context={'user_id': request.user.id, 'superuser': request.user.is_superuser})
        return Response(serializer.data, status=status.HTTP_200_OK)


class WalletCouponsView(ListAPIView):
    serializer_class = UserBoughtCodesSerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [SearchFilter, TimeFilter]
    search_fields = ['business__title', 'category__title', 'linecoupon__title', 'title']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            business = Business.objects.all()
        else:
            business = Business.objects.filter(admin_id=user.id)
        sold_coupons = (
            Coupon.objects.filter(business__in=business, linecoupon__closedbasketdetail__closedbasket__status=3)
            .distinct("id").annotate(
                days_left=F('expire_date'),
                user_first_name=F('linecoupon__closedbasketdetail__closedbasket__user__first_name'),
                user_last_name=F('linecoupon__closedbasketdetail__closedbasket__user__last_name'),
                status=F('linecoupon__closedbasketdetail__closedbasket__is_paid')
            ))
        return sold_coupons

    def get_serializer_context(self):
        user_id = self.request.user.id
        context = super().get_serializer_context()
        context['user_id'] = user_id
        return context

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).distinct("slug")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

