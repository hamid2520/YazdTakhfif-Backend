from datetime import datetime, timedelta

from rest_framework.filters import BaseFilterBackend


class TimeFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        time = request.query_params.get("time")
        time_format = datetime.today()
        if time:
            if time.lower() == 'today':
                queryset.filter(linecoupon__closedbasketdetail__closedbasket__payment_datetime__contains=time_format)
            elif time.lower() == 'week':
                time_format = (time_format - timedelta(weeks=1))
                queryset.filter(linecoupon__closedbasketdetail__closedbasket__payment_datetime__gte=time_format)
            elif time.lower() == 'month':
                time_format = (time_format - timedelta(days=30))
                queryset.filter(linecoupon__closedbasketdetail__closedbasket__payment_datetime__gte=time_format)
        return queryset
