import logging

from azbankgateways import bankfactories, models as bank_models, default_settings as settings
from azbankgateways.exceptions import AZBankGatewaysException
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import redirect, render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from src.payment.serializers import PaymentSerializer
from .models import OnlinePayment, Gateway
from .permissions import IsOwnerOrSuperUser
from ..basket.models import Basket

GATEWAY_STATUS_TOKEN_INVALID = 1
GATEWAY_STATUS_PROBLEM_CONNECT_GATEWAY = 2
GATEWAY_STATUS_SUCCESS = 3
GATEWAY_STATUS_NOT_SUCCESS = 4
GATEWAY_STATUS_NOT_SUCCESS_PAYMENT = 5
GATEWAY_NOT_VALID = 6
BASKET_NOT_FOUND = 7
INVOICE_NOT_FOUND = 7
GATEWAY_ERRORS = {
    GATEWAY_STATUS_TOKEN_INVALID: "!توکن نا معتبر است",
    GATEWAY_STATUS_PROBLEM_CONNECT_GATEWAY: "!مشکل در اتصال به درگاه پرداخت",
    GATEWAY_STATUS_SUCCESS: "پرداخت موفق",
    GATEWAY_STATUS_NOT_SUCCESS: "!پرداخت ناموفق",
    GATEWAY_STATUS_NOT_SUCCESS_PAYMENT: """پرداخت موفق نبوده است.
     اگر پول کم شده است ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت.""",
    GATEWAY_NOT_VALID: "!درگاه وارد شده معتبر نیست",
    BASKET_NOT_FOUND: "!سبد خرید یافت نشد",
    INVOICE_NOT_FOUND: "!فاکتور یافت نشد"
}


def go_to_gateway_view_v2(request, slug):
    try:
        basket = Basket.objects.get(slug=slug)
    except ObjectDoesNotExist:
        return redirect(
            reverse(viewname="payment_result", args=["00000000-0000-0000-0000-000000000000", BASKET_NOT_FOUND]))
    basket_count_validation_status = basket.final_count_validation()
    if basket_count_validation_status:
        return redirect(reverse(viewname='final_count_validation', args=[basket.slug, ]))
    gateway_name = request.GET.get("gateway")
    try:
        gateway = Gateway.objects.get(name="IDPAY", active=True)
    except ObjectDoesNotExist:
        return redirect(
            reverse(viewname="payment_result", args=["00000000-0000-0000-0000-000000000000", GATEWAY_NOT_VALID]))
    op = OnlinePayment.objects.create(user_id=basket.user.id, gateway_id=gateway.id, payment_id=basket.id)
    op.save()
    amount = int(op.payment.total_price_with_offer)
    user_mobile_number = request.user.username
    client_callback_url = reverse(viewname='callback-gateway-v2', args=[op.token])
    factory = bankfactories.BankFactory()
    try:
        bank = factory.create(bank_type=op.gateway.gateway)
        bank.set_request(request)
        bank.set_amount(amount)
        bank.set_client_callback_url(client_callback_url)
        bank.set_mobile_number(user_mobile_number)
        bank_record = bank.ready()
        return bank.redirect_gateway()
    except AZBankGatewaysException as e:
        return redirect(reverse(viewname="payment_result", args=[op.token, GATEWAY_STATUS_PROBLEM_CONNECT_GATEWAY]))


def callback_gateway_view_v2(request, token):
    try:
        op = OnlinePayment.objects.get(token=token)
    except ObjectDoesNotExist:
        return redirect(
            reverse(viewname="payment_result", args=["00000000-0000-0000-0000-000000000000", INVOICE_NOT_FOUND]))
    if True:
        # if op.user_id == request.user.id or request.user.is_superuser:
        tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM)
        if not tracking_code:
            logging.debug("این لینک معتبر نیست.")
            return redirect(
                reverse(viewname="payment_result", args=["00000000-0000-0000-0000-000000000000", INVOICE_NOT_FOUND]))

        try:
            bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
        except bank_models.Bank.DoesNotExist:
            logging.debug("این لینک معتبر نیست.")
            return redirect(
                reverse(viewname="payment_result", args=["00000000-0000-0000-0000-000000000000", INVOICE_NOT_FOUND]))
        # در این قسمت باید از طریق داده هایی که در بانک رکورد وجود دارد، رکورد متناظر یا هر اقدام مقتضی دیگر را انجام دهیم
        if bank_record.is_success:
            response = {"pre_confirm": {"Status": "OK", "Authority": ""}, "post_confirm": {
                "RefID": bank_record.reference_number, "Status": bank_record.status}}
            op.response = response
            op.status = op.STATUS_SUCCESS
            op.save()
            return redirect(reverse(
                viewname='payment_result',
                args=[token, GATEWAY_STATUS_SUCCESS]))

        op.status = op.STATUS_NOT_SUCCESS
        response = {"pre_confirm": {"Status": bank_record.is_success, "Authority": ""}, "post_confirm": {
            "RefID": bank_record.reference_number, "Status": bank_record.status}}
        op.response = response
        op.save()
        # پرداخت موفق نبوده است. اگر پول کم شده است ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت.
        return redirect(reverse(
            viewname='payment_result',
            args=[token, GATEWAY_STATUS_NOT_SUCCESS_PAYMENT]))
    return redirect(
        reverse(viewname="payment_result", args=["00000000-0000-0000-0000-000000000000", INVOICE_NOT_FOUND]))


def payment_result(request, token, status):
    try:
        op = OnlinePayment.objects.filter(token=token)
        if op.exists():
            op = op.first()
            if True:
                # if op.user_id == request.user.id or request.user.is_superuser:
                context = {
                    "ref_id": op.ref_id,
                    "status": status,
                    "message": GATEWAY_ERRORS[status],
                }
                # create payment
                if op.status == op.STATUS_SUCCESS:
                    data = {
                        "user": op.user.id,
                        "basket_id": op.payment.slug
                    }
                    payment_serializer = PaymentSerializer(data=data)
                    if payment_serializer.is_valid():
                        payment_serializer.save()
                    else:
                        context["status"] = GATEWAY_STATUS_NOT_SUCCESS
                        context["message"] = "!پرداخت شما نهایی نشده است. لطفا با پشتیبانی تماس بگیرید"
                        context["errors"] = payment_serializer.errors
                return render(request, template_name="payment_gateway/payment-result.html", context=context)
            raise Http404("!فاکتور یافت نشد")
        context = {
            "message": GATEWAY_ERRORS[status],
        }
        return render(request, template_name="payment_gateway/payment-result.html", context=context)
    except Exception:
        raise Http404


class BasketCountValidationAPIView(APIView):
    permission_classes = [IsOwnerOrSuperUser, ]

    def get(self, request, basket_slug):
        try:
            basket = Basket.objects.get(slug=basket_slug)
            self.check_object_permissions(request, basket)
            basket_count_status = basket.final_count_validation()
            data = {
                "product": basket_count_status
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
