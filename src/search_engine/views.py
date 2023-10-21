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
        try:
            category_search_date = Category.objects.filter(title__contains=text).values('title')
            coupon_search_date = Coupon.objects.filter(title__contains=text).values('title')
            line_coupon_search_date = LineCoupon.objects.filter(title__contains=text).values('title')

            category_search_date = category_search_date.annotate(model_name=Value('category', output_field=CharField()))
            coupon_search_date = coupon_search_date.annotate(model_name=Value('coupon', output_field=CharField()))
            line_coupon_search_date = line_coupon_search_date.annotate(
                model_name=Value('line_coupon', output_field=CharField()))

            result_queryset = chain(category_search_date, coupon_search_date, line_coupon_search_date)
            data = list(result_queryset)

            return Response(data, status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
