from datetime import timedelta
import jdatetime

from django.utils import timezone
from rest_framework.filters import BaseFilterBackend


class TimeFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        time = request.query_params.get("time")
        now = timezone.now()
        tomorrow = now + timedelta(days=1)
        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            next_month = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        if time:
            if time.lower() == 'today':
                queryset = queryset.filter(linecoupon__closedbasketdetail__closedbasket__created_at__date=now.date())
            elif time.lower() == 'week':
                queryset = queryset.filter(
                    linecoupon__closedbasketdetail__closedbasket__created_at__date__gte=now - timedelta(days=7),
                    linecoupon__closedbasketdetail__closedbasket__created_at__date__lte=now)
            elif time.lower() == 'month':
                queryset = queryset.filter(
                    linecoupon__closedbasketdetail__closedbasket__created_at__date__gte=now.replace(day=1, hour=0,
                                                                                                    minute=0, second=0,
                                                                                                    microsecond=0),
                    linecoupon__closedbasketdetail__closedbasket__created_at__date__lte=next_month)
        return queryset


class CustomTimeFilter:
    @staticmethod
    def filter_line_coupon(queryset, time):
        now = timezone.now()
        print(now)
        tomorrow = now + timedelta(days=1)
        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            next_month = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        if time:
            if time.lower() == 'today':
                queryset = queryset.filter(closedbasketdetail__closedbasket__created_at__date=now.date())
            elif time.lower() == 'week':
                queryset = queryset.filter(
                    closedbasketdetail__closedbasket__created_at__date__gte=now - timedelta(days=7),
                    closedbasketdetail__closedbasket__created_at__date__lte=now)
            elif time.lower() == 'month':
                queryset = queryset.filter(
                    closedbasketdetail__closedbasket__created_at__date__gte=now.replace(day=1, hour=0,
                                                                                        minute=0, second=0,
                                                                                        microsecond=0),
                    closedbasketdetail__closedbasket__created_at__date__lte=next_month)
        return queryset.filter(closedbasketdetail__closedbasket__status=3)

    @staticmethod
    def filter_basket_detail(queryset, time):
        now = timezone.now()
        print(now)
        tomorrow = now + timedelta(days=1)
        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            next_month = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        if time:
            if time.lower() == 'today':
                queryset = queryset.filter(closedbasket__created_at__date=now.date())
            elif time.lower() == 'week':
                queryset = queryset.filter(
                    closedbasket__created_at__date__gte=now - timedelta(days=7),
                    closedbasket__created_at__date__lte=now)
            elif time.lower() == 'month':
                queryset = queryset.filter(
                    closedbasket__created_at__date__gte=now.replace(day=1, hour=0,
                                                                    minute=0, second=0,
                                                                    microsecond=0),
                    closedbasket__created_at__date__lte=next_month)
        return queryset.filter(closedbasket__status=3)

    @staticmethod
    def filter_product_codes(queryset, time):
        now = timezone.now()
        print(now)
        tomorrow = now + timedelta(days=1)
        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            next_month = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        if time:
            if time.lower() == 'today':
                queryset = queryset.filter(closed_basket__created_at__date=now.date())
            elif time.lower() == 'week':
                queryset = queryset.filter(
                    closed_basket__created_at__date__gte=now - timedelta(days=7),
                    closed_basket__created_at__date__lte=now)
            elif time.lower() == 'month':
                queryset = queryset.filter(
                    closed_basket__created_at__date__gte=now.replace(day=1, hour=0,
                                                                    minute=0, second=0,
                                                                    microsecond=0),
                    closed_basket__created_at__date__lte=next_month)
        return queryset.filter(closed_basket__status=3)
