import logging

from azbankgateways.exceptions import AZBankGatewaysException
from azbankgateways import bankfactories, models as bank_models, default_settings as settings
from django.apps import apps
from django.db import models
from django.http import Http404
from django.shortcuts import redirect, render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404

from .models import OnlinePayment, Gateway
from src.payment.models import Payment
from src.wallet.models import Transaction
from src.payment.serializers import PaymentSerializer
from django.core.exceptions import ObjectDoesNotExist

from .permissions import IsOwnerOrSuperUser
from ..basket.models import Basket

GATEWAY_STATUS_TOKEN_INVALID = 1
GATEWAY_STATUS_PROBLEM_CONNECT_GATEWAY = 2
GATEWAY_STATUS_SUCCESS = 3
GATEWAY_STATUS_NOT_SUCCESS = 4
GATEWAY_STATUS_NOT_SUCCESS_PAYMENT = 5
GATEWAY_NOT_VALID = 6
GATEWAY_ERRORS = {
    GATEWAY_STATUS_TOKEN_INVALID: "توکن نا معتبر است!",
    GATEWAY_STATUS_PROBLEM_CONNECT_GATEWAY: "مشکل در اتصال به درگاه پرداخت!",
    GATEWAY_STATUS_SUCCESS: "پرداخت موفق",
    GATEWAY_STATUS_NOT_SUCCESS: "پرداخت ناموفق!",
    GATEWAY_STATUS_NOT_SUCCESS_PAYMENT: """پرداخت موفق نبوده است.
     اگر پول کم شده است ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت.""",
    GATEWAY_NOT_VALID: "درگاه وارد شده معتبر نیست!"
}


def go_to_gateway_view_v2(request, basket_slug):
    try:
        basket = Basket.objects.get(slug=basket_slug)
    except ObjectDoesNotExist:
        raise Http404
    # if basket.user_id == request.user.id or request.user.is_superuser:
    if True:
        basket_count_validation_status = basket.final_count_validation()
        if basket_count_validation_status:
            return redirect(
                reverse('final_count_validation', args=[basket.slug, ]))
        gateway_name = request.GET.get("gateway")
        try:
            gateway = Gateway.objects.get(gateway=gateway_name, active=True)
        except ObjectDoesNotExist:
            return redirect(reverse('payment_result', args=["00000000-0000-0000-0000-000000000000", GATEWAY_NOT_VALID]))
        op = OnlinePayment.objects.exclude(payment_id=basket.id,gateway_id=gateway.id,status=3)
        if op.exists():
            op = op.first()
        else:
            op = OnlinePayment.objects.create(user=request.user, gateway=gateway, payment=basket)
            op.save()
        amount = int(op.payment.total_price_with_offer)
        user_mobile_number = +989138528929
        client_callback_url = reverse('callback-gateway-v2', args=[op.token])
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
            return redirect(reverse("payment_result", args=[op.token, GATEWAY_STATUS_PROBLEM_CONNECT_GATEWAY]))
    raise Http404()


def callback_gateway_view_v2(request, token):
    try:
        op = OnlinePayment.objects.get(token=token)
    except ObjectDoesNotExist:
        raise Http404
    if op.user_id == request.user.id or request.user.is_superuser:
        tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM)
        if not tracking_code:
            logging.debug("این لینک معتبر نیست.")
            raise Http404

        try:
            bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
        except bank_models.Bank.DoesNotExist:
            logging.debug("این لینک معتبر نیست.")
            raise Http404
        # در این قسمت باید از طریق داده هایی که در بانک رکورد وجود دارد، رکورد متناظر یا هر اقدام مقتضی دیگر را انجام دهیم
        if bank_record.is_success:
            response = {"pre_confirm": {"Status": "OK", "Authority": ""}, "post_confirm": {
                "RefID": bank_record.reference_number, "Status": bank_record.status}}
            op.response = response
            op.status = op.STATUS_SUCCESS
            op.save()
            # if op.payment.payment_type == Payment.TYPE_CHARGE:
            #     new_balance = op.payment.total
            #     to_data = Account.objects.filter(
            #         owner=op.user, type=Account.TYPE_CHARGE).first()
            #     from_data = Account.objects.filter(id=101).first()
            #     if not to_data:
            #         to_data = Account.objects.create(
            #             balance=0, type=Account.TYPE_CHARGE, owner=op.user)
            #     Transaction.add_transaction(
            #         from_data, to_data, Account.TYPE_CHARGE, new_balance)
            #     pay_last = op.payment.finalize_after_charge
            #     if pay_last:
            #         if account.get_account_balance(op.user, 'total') >= pay_last.total:
            #             account.modify_account_balance(
            #                 op.user, pay_last.total)
            #             pay_last.finalize()
            #             op.payment.finalize_charge()
            #         else:
            #             op.payment.finalize_charge()
            #             Payment.objects.filter(pk=op.payment.finalize_after_charge.id).update(
            #                 status=Payment.STATUS_FAILED)
            #             op.status = op.STATUS_NOT_SUCCESS
            #             response = {"pre_confirm": {"Status": bank_record.is_success, "Authority": ""}, "post_confirm": {
            #                 "RefID": bank_record.reference_number, "Status": bank_record.status}}
            #             op.response = response
            #             op.save()
            #             # Campaign.send_template_sms(
            #             #     to=op.user.usermeta.phone,
            #             #     tpl='failPayment',
            #             #     context={
            #             #         'token': op.user.first_name + " " + "عزیز",
            #             #         'token2': op.payment.id,
            #             #     },
            #             #     priority=Campaign.PRIORITY_CRITICAL
            #             # )
            #             # Message = apps.get_model('notification', 'Message')
            #             # Message.objects.create(recipient_user=op.user, is_read=False,
            #             #                        title="!پرداخت ناموفق", content=op.payment.id)
            #             return redirect(reverse('payment_result', args=[token, GATEWAY_STATUS_NOT_SUCCESS]))
            #     else:
            #         try:
            #             op.payment.finalize_charge()
            #         except Exception as e:
            #             raise Exception(op.FAILED_CODE_FINALIZE)
            # else:
            #     try:
            #         op.payment.finalize_charge()
            #     except Exception as e:
            #         raise Exception(op.FAILED_CODE_FINALIZE)

            # Campaign.send_template_sms(
            #     to=op.user.usermeta.phone,
            #     tpl='successfulPayment',
            #     context={
            #         'token': op.user.first_name + " " + "عزیز",
            #         'token2': op.payment.id,
            #     },
            #     priority=Campaign.PRIORITY_CRITICAL
            # )
            # Message = apps.get_model('notification', 'Message')
            # Message.objects.create(
            #     recipient_user=op.user, is_read=False, title="پرداخت موفق", content=op.payment.id)

            return redirect(reverse(
                'payment_result',
                args=[token, GATEWAY_STATUS_SUCCESS]))

        op.status = op.STATUS_NOT_SUCCESS
        response = {"pre_confirm": {"Status": bank_record.is_success, "Authority": ""}, "post_confirm": {
            "RefID": bank_record.reference_number, "Status": bank_record.status}}
        op.response = response
        op.save()
        # Campaign.send_template_sms(
        #     to=op.user.usermeta.phone,
        #     tpl='failPayment',
        #     context={
        #         'token': op.user.first_name + " " + "عزیز",
        #         'token2': op.payment.id,
        #     },
        #     priority=Campaign.PRIORITY_CRITICAL
        # )
        # Message = apps.get_model('notification', 'Message')
        # Message.objects.create(recipient_user=op.user, is_read=False,
        #                        title="پرداخت ناموفق", content=op.payment.id)
        # پرداخت موفق نبوده است. اگر پول کم شده است ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت.
        return redirect(reverse(
            viewname='payment_result',
            args=[token, GATEWAY_STATUS_NOT_SUCCESS_PAYMENT]))
    raise Http404


def payment_result(request, token, status):
    op = OnlinePayment.objects.filter(token=token)
    if op.exists():
        op = op.first()
        if op.user_id == request.user.id or request.user.is_superuser:
            context = {
                "user": op.user.username,
                "obj": op,
                "status": status,
                "message": GATEWAY_ERRORS[status],
            }
            # create payment
            if op.status == op.STATUS_SUCCESS:
                data = {
                    "user": op.user.id,
                    "basket_id": op.payment.id
                }
                payment_serializer = PaymentSerializer(data=data)
                if payment_serializer.is_valid():
                    payment_serializer.save()
                else:
                    context["status"] = GATEWAY_STATUS_NOT_SUCCESS
                    context["message"] = "پرداخت شما نهایی نشده است. لطفا با پشتیبانی تماس بگیرید!"
            return render(request, "payment_gateway/payment-result.html", context)
        raise Http404
    context = {
        "message": GATEWAY_ERRORS[status],
    }
    return render(request, "payment_gateway/payment-result.html", context)


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
