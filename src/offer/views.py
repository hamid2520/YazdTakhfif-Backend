from django.db.models import Sum
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import render

from .models import Offer
from ..basket.models import Basket, ClosedBasket
from .filters import IsSuperUserOrOwner
from .serializers import OfferSerializer, OfferValidatorSerializer

from django.http import HttpResponse
from django.template.loader import get_template, render_to_string
from weasyprint import HTML


class OfferViewSet(ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    lookup_field = "offer_code"
    lookup_url_kwarg = "offer_code"
    filter_backends = [IsSuperUserOrOwner, ]

    @action(detail=False, methods=["POST", ], url_path="validate-offer", url_name="validate_offer")
    def validate_offer(self, offer_code):
        serializer = OfferValidatorSerializer(data=self.request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            offer = Offer.objects.get(offer_code=data.get("offer_code"))
            basket = Basket.objects.get(slug=data.get("basket_slug"))
            products_total_price = basket.product.filter(
                line_coupon__coupon__business__in=offer.limited_businesses.all()).aggregate(
                total_offered_products_price=Sum("total_price_with_offer"))["total_offered_products_price"]
            offered_price = basket.total_price_with_offer - ((products_total_price * offer.percent) // 100)
            data = {
                "offer_percent": offer.percent,
                "offered_price": offered_price,
            }
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def html_to_pdf(request, slug):
    basket = ClosedBasket.objects.prefetch_related("product").get(slug=slug)
    basket_products = basket.product.all()
    html_content = render_to_string(template_name="offer/pdf.html", context={"basket": basket,
                                                                             "basket_products": basket_products})
    # Get the HTML content from a template
    # template = get_template('offer/pdf.html')
    # html_content = template.render()

    # Generate PDF from the HTML content
    pdf_file = HTML(string=html_content,).write_pdf()


    # Create an HTTP response with PDF content and a 'Content-Type' header
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="output.pdf"'
    return response
# def html_to_pdf(request, slug):
#     basket = ClosedBasket.objects.prefetch_related("product").get(slug=slug)
#     basket_products = basket.product.all()
#     # html_content = render_to_string(template_name="offer/pdf.html", context={"basket": basket,
#     #                                                                          "basket_products": basket_products})
#     # Get the HTML content from a template
#     # template = get_template('offer/pdf.html')
#     # html_content = template.render()
#
#     # Generate PDF from the HTML content
#     # pdf_file = HTML(string=html_content).write_pdf()
#
#     # Create an HTTP response with PDF content and a 'Content-Type' header
#     # response = HttpResponse(pdf_file, content_type='application/pdf')
#     # response['Content-Disposition'] = 'attachment; filename="output.pdf"'
#     return render(request, "offer/pdf.html", context={"basket": basket,
#                                                       "basket_products": basket_products})
