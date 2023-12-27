from datetime import datetime, timedelta

from rest_framework.filters import BaseFilterBackend


class TimeFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        time = request.query_params.get("time")
        time_format = datetime.today()
        filter_var = None
        if time:
            if time.lower() == 'today':
                filter_var = time_format
            elif time.lower() == 'week':
                filter_var = (time_format - timedelta(weeks=1))
            elif time.lower() == 'month':
                filter_var = (time_format - timedelta(days=30))
                
            queryset.filter(linecoupon__closedbasketdetail__closedbasket__payment_datetime__gte=filter_var)
        return queryset
