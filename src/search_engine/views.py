from django.db.models import Value, CharField
from rest_framework import status
from rest_framework.request import Request
from rest_framework.decorators import APIView
from rest_framework.response import Response
from itertools import chain
from src.coupon.models import Category, Coupon, LineCoupon


# Create your views here.

class SearchEngineListApiView(APIView):

    def get(self, request: Request, text):
        category_search_data = Category.objects.filter(title__contains=text).values('title', 'slug').annotate(
            model_name=Value('category', output_field=CharField()))
        coupon_search_data = Coupon.objects.filter(title__contains=text).values('title', 'slug').annotate(
            model_name=Value('coupon', output_field=CharField()))
        line_coupon_search_data = LineCoupon.objects.filter(title__contains=text).values('title', 'slug').annotate(
            model_name=Value('line_coupon', output_field=CharField()))

        if (category_search_data is not None) and (coupon_search_data is not None) and (
                line_coupon_search_data is not None):
            result_queryset = chain(category_search_data, coupon_search_data, line_coupon_search_data)
            data = list(result_queryset)

            return Response(data, status.HTTP_200_OK)

        return Response(status=status.HTTP_404_NOT_FOUND)
