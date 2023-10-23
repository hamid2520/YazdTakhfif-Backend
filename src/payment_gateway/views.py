import logging

from azbankgateways.exceptions import AZBankGatewaysException
from azbankgateways import bankfactories, models as bank_models, default_settings as settings
from django.apps import apps
from django.http import Http404
from django.shortcuts import redirect, render
from rest_framework.reverse import reverse

from .models import OnlinePayment
from src.payment.models import Payment
from src.wallet.models import Account, Transaction
from src.wallet import account
from src.payment.serializers import PaymentSerializer

GATEWAY_STATUS_TOKEN_INVALID = 1
GATEWAY_STATUS_PROBLEM_CONNECT_GATEWAY = 2
GATEWAY_STATUS_SUCCESS = 3
GATEWAY_STATUS_NOT_SUCCESS = 4
GATEWAY_STATUS_NOT_SUCCESS_PAYMENT = 5
GATEWAY_ERRORS = {
    GATEWAY_STATUS_TOKEN_INVALID: "توکن نا معتبر است!",
    GATEWAY_STATUS_PROBLEM_CONNECT_GATEWAY: "مشکل در اتصال به درگاه پرداخت!",
    GATEWAY_STATUS_SUCCESS: "پرداخت موفق",
    GATEWAY_STATUS_NOT_SUCCESS: "پرداخت ناموفق!",
    GATEWAY_STATUS_NOT_SUCCESS_PAYMENT: """پرداخت موفق نبوده است.
     اگر پول کم شده است ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت."""
}


def go_to_gateway_view_v2(request, token):
    op = OnlinePayment.objects.filter(token=token).first()
    if op.status != 1:
        return redirect(reverse('payment_result', args=[token, GATEWAY_STATUS_TOKEN_INVALID]))
    amount = int(op.payment.total_price_with_offer)
    user_mobile_number = +989138528929
    client_callback_url = reverse('callback-gateway-v2', args=[token])
    factory = bankfactories.BankFactory()
    try:
        bank = factory.create()
        bank.set_request(request)
        bank.set_amount(amount)
        bank.set_client_callback_url(client_callback_url)
        bank.set_mobile_number(user_mobile_number)
        bank_record = bank.ready()
        return bank.redirect_gateway()
    except AZBankGatewaysException as e:
        logging.critical(e)
        redirect(reverse("payment_result", args=[token, GATEWAY_STATUS_PROBLEM_CONNECT_GATEWAY]))
        raise e


def callback_gateway_view_v2(request, token):
    op = OnlinePayment.objects.filter(token=token).first()
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


def payment_result(request, token, status):
    op = OnlinePayment.objects.filter(token=token)
    if op.exists():
        op = op.first()
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
                print(payment_serializer.errors)
                context["status"] = GATEWAY_STATUS_NOT_SUCCESS
                context["message"] = "پرداخت شما نهایی نشده است. لطفا با پشتیبانی تماس بگیرید!"
        return render(request, "payment_gateway/payment-result.html", context)
    raise Http404
