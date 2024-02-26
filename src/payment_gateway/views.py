import logging

from azbankgateways import bankfactories, models as bank_models, default_settings as settings
from azbankgateways.exceptions import AZBankGatewaysException
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from jdatetime import datetime
from django.utils import timezone

from src.payment.serializers import PaymentSerializer
from .models import OnlinePayment, Gateway
from .permissions import IsOwnerOrSuperUser
from ..basket.models import Basket
from ..basket.serializers import BasketShowSerializer, ClosedBasketShowSerializer

HostUrl = 'http://158.255.74.252:3000'
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
     درصورت کسر مبلغ از حساب شما ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت.""",
    GATEWAY_NOT_VALID: "!درگاه وارد شده معتبر نیست",
    BASKET_NOT_FOUND: "!سبد خرید یافت نشد",
    INVOICE_NOT_FOUND: "!فاکتور یافت نشد"
}


def go_to_gateway_view_v2(request, slug):
    try:
        basket = Basket.objects.get(slug=slug)
    except ObjectDoesNotExist:
        return redirect(f"{HostUrl}/factor?status={BASKET_NOT_FOUND}")
    basket_count_validation_status = basket.final_count_validation()
    if basket_count_validation_status:
        return redirect(reverse(viewname='final_count_validation', args=[basket.slug, ]))
    gateway_name = request.GET.get("gateway")
    try:
        gateway = Gateway.objects.get(name="MELLAT", active=True)
    except ObjectDoesNotExist:
        return redirect(f"{HostUrl}/factor?status={GATEWAY_NOT_VALID}")
    op = OnlinePayment.objects.exclude(status=OnlinePayment.STATUS_SUCCESS).filter(user__id=basket.user_id,
                                                                                   payment_id=basket.id)
    if op.exists():
        op = op.first()
        op.gateway_id = gateway.id
    else:
        op = OnlinePayment.objects.create(user_id=basket.user.id, gateway_id=gateway.id, payment_id=basket.id)
    op.save()
    amount = int(op.payment.total_price_with_offer)
    user_mobile_number = basket.user.username
    client_callback_url = reverse(viewname='callback-gateway-v2', args=[op.token])
    factory = bankfactories.BankFactory()
    try:
        bank = factory.create(bank_type="MELLAT")
        bank.set_request(request)
        bank.set_amount(amount * 10)
        bank.set_client_callback_url(client_callback_url)
        bank.set_mobile_number(user_mobile_number)
        bank_record = bank.ready()
        return bank.redirect_gateway()
    except AZBankGatewaysException as e:
        print(e)
        return redirect(
            f"{HostUrl}/factor?status={GATEWAY_STATUS_PROBLEM_CONNECT_GATEWAY}")


def callback_gateway_view_v2(request, token):
    try:
        op = OnlinePayment.objects.get(token=token)
    except ObjectDoesNotExist:
        return redirect(f"{HostUrl}/factor?status={INVOICE_NOT_FOUND}")
    if True:
        tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM)
        if not tracking_code:
            logging.debug("این لینک معتبر نیست.")
            return redirect(f"{HostUrl}/factor?status={INVOICE_NOT_FOUND}")
        try:
            bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
        except bank_models.Bank.DoesNotExist:
            logging.debug("این لینک معتبر نیست.")
            return redirect(f"{HostUrl}/factor?status={INVOICE_NOT_FOUND}")
        # در این قسمت باید از طریق داده هایی که در بانک رکورد وجود دارد، رکورد متناظر یا هر اقدام مقتضی دیگر را انجام دهیم
        if bank_record.is_success:
            response = {"pre_confirm": {"Status": "OK", "Authority": ""}, "post_confirm": {
                "RefID": bank_record.reference_number, "Status": bank_record.status}}
            op.response = response
            op.status = op.STATUS_SUCCESS
            op.save()
            return redirect(f"{HostUrl}/factor?status={GATEWAY_STATUS_SUCCESS}")

        op.status = op.STATUS_NOT_SUCCESS
        response = {"pre_confirm": {"Status": bank_record.is_success, "Authority": ""}, "post_confirm": {
            "RefID": bank_record.reference_number, "Status": bank_record.status}}
        op.response = response
        op.save()
        # پرداخت موفق نبوده است. اگر پول کم شده است ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت.
        return redirect(f"{HostUrl}/factor?status={GATEWAY_STATUS_NOT_SUCCESS_PAYMENT}")


class PaymentResultAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, payment_status):
        try:
            user = request.user
            op = OnlinePayment.objects.filter(user__id=user.id)
            if op.exists():
                op = op.last()
                if op.user_id == request.user.id or request.user.is_superuser:
                    payment_datetime = datetime.fromgregorian(datetime=timezone.now())

                    context = {
                        "ref_id": op.ref_id,
                        "datetime": payment_datetime.strftime("%Y/%m/%d %H:%M:%S"),
                        "status": payment_status,
                        "gifted": op.payment.gifted if op.payment else op.closed_basket.gifted,
                        "message": GATEWAY_ERRORS[payment_status],
                        "user": {
                            "first_name": user.first_name,
                            "last_name": user.last_name,
                            "phone": user.username,
                            "email": user.email,
                        }
                    }
                    # create payment
                    if op.status == op.STATUS_SUCCESS:
                        if op.payment:
                            data = {
                                "user": op.user.id,
                                "basket_id": op.payment.slug
                            }
                            payment_serializer = PaymentSerializer(data=data)
                            if payment_serializer.is_valid():
                                payment_serializer.save()
                            else:
                                context["message"] = "!پرداخت شما نهایی نشده است. لطفا با پشتیبانی تماس بگیرید"
                                context["errors"] = payment_serializer.errors
                    return Response(data=context, status=status.HTTP_200_OK)
                return Response(status=status.HTTP_404_NOT_FOUND)
            context = {
                "message": GATEWAY_ERRORS[payment_status],
            }
            return Response(data=context, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentBasketAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        user = request.user
        op = OnlinePayment.objects.filter(user__id=user.id)
        if op.exists():
            op = op.last()
            if op.payment:
                serializer = BasketShowSerializer(instance=op.payment)
            else:
                serializer = ClosedBasketShowSerializer(instance=op.closed_basket)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


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
