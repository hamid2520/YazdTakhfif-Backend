from django.db.models import Value, CharField
from rest_framework import status
from rest_framework.request import Request
from rest_framework.decorators import APIView
from rest_framework.response import Response
from itertools import chain, count
from src.coupon.models import Category, Coupon, LineCoupon
from .serializers import SearchEngineApiSerializer

# Create your views here.

class SearchEngineListApiView(APIView):

    def get(self, request: Request, text):
        category_search_data = Category.objects.filter(title__icontains=text).values('title', 'slug').annotate(
            model_name=Value('category', output_field=CharField()))
        coupon_search_data = Coupon.objects.filter(title__icontains=text).values('title', 'slug').annotate(
            model_name=Value('coupon', output_field=CharField()))
        line_coupon_search_data = LineCoupon.objects.filter(title__icontains=text).values('title', 'slug').annotate(
            model_name=Value('line_coupon', output_field=CharField()))

        if (category_search_data.count() == 0) and (coupon_search_data.count() == 0) and (line_coupon_search_data.count() == 0):
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        result_queryset = chain(category_search_data, coupon_search_data, line_coupon_search_data)
        serializer = SearchEngineApiSerializer
        data = serializer(instance=result_queryset, many=True)
        
        return Response(serializer.data, status.HTTP_200_OK)

        
'''
without data 
HTTP 404 Not Found
Allow: GET, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept
'''
'''
with data

HTTP 200 OK
Allow: GET, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

[
    {
        "title": "test_cat",
        "slug": "test_cat",
        "model_name": "category"
    }
]
'''