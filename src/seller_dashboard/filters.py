from datetime import timedelta

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
                queryset = queryset.filter(created_at__date=now.date())
            elif time.lower() == 'week':
                queryset = queryset.filter(
                    created_at__date__gte=now - timedelta(days=7),
                    created_at__date__lte=now)
            elif time.lower() == 'month':
                queryset = queryset.filter(
                    created_at__date__gte=now.replace(day=1, hour=0,
                                                      minute=0, second=0,
                                                      microsecond=0),
                    created_at__date__lte=next_month)
        return queryset
