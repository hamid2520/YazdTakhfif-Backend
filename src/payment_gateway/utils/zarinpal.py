import logging

from django.conf import settings
from django.db import transaction
from rest_framework.reverse import reverse

from zeep.transports import Transport
from zeep import Client

logger = logging.getLogger('django')


def goto_gateway(op):
    """
    @param OnlinePayment op:
    @return :
    """
    MERCHANT_ID = op.gateway.data['MID']
    callbackURL = settings.API_BASEURL + reverse('online-payment-callback', args=[op.token])
    amount = int(op.payment.total)  # Toman / Required
    description = "خرید محصول از یزدتخفیف"  # Required
    email = op.user.email or ''  # Optional
    mobile = op.user.usermeta.phone  # Optional
    _status = False
    try:
        transport = Transport(timeout=5)
        client = Client(settings.ZARINPAL['WEBSERVICE_URL'], transport=transport)
        result = client.service.PaymentRequest(MERCHANT_ID, amount, description, email, mobile, callbackURL)
        # result.Authority شناسه ۳۶ کاراکتری یونیک به ازای هر درخواست پرداخت ایجاد می‌شود
        op.extra_data = result.__dict__['__values__']
        op.save()
    except:
        op.failed_code = op.get_failed_code_choices_dictionary()[op.FAILED_CODE_GATEWAY_CONNECTION]
        op.status = op.STATUS_FAILED
        op.save()
    else:
        if result.Status == 100:
            _status = True
            op.status = op.STATUS_PENDING
            op.save()
        else:
            op.failed_code = op.get_failed_code_choices_dictionary()[op.FAILED_CODE_GOTO_GATEWAY]
            op.status = op.STATUS_FAILED
            op.save()
    return _status, op


def verify_payment(op, request):
    """
    @param OnlinePayment op:
    @param request:
    @return:
    """
    MERCHANT_ID = op.gateway.data['MID']
    authority = request.GET['Authority']
    _status = request.GET.get('Status')
    response = {
        'pre_confirm': {
            'Status': _status,
            'Authority': authority
        },
        'post_confirm': {}
    }
    op.response = response
    op.save()

    exception_msg = ''
    verification_status = False

    if _status != 'OK':
        op.status = op.STATUS_FAILED
        op.failed_code = op.get_failed_code_choices_dictionary()[op.FAILED_CODE_PRE_CONFIRM]
        op.save()
    else:
        try:
            with transaction.atomic():
                try:
                    op.finalize()
                except Exception as e:
                    exception_msg = str(e)
                    raise Exception(op.FAILED_CODE_FINALIZE)

                try:
                    transport = Transport(timeout=5)
                    client = Client(settings.ZARINPAL['WEBSERVICE_URL'], transport=transport)
                    amount = int(op.payment.total)
                    result = client.service.PaymentVerification(MERCHANT_ID, authority, amount)
                    response['post_confirm'] = result.__dict__['__values__']
                    op.response = response
                    op.save()
                except Exception as e:
                    exception_msg = str(e)
                    raise Exception(op.FAILED_CODE_GATEWAY_CONNECTION)

                if result.Status == 100:
                    op.ref_id = result.RefID
                    op.save()
                    verification_status = True
                elif result.Status == 101:
                    raise Exception('This payment has already been verified.')
                else:
                    raise Exception(op.FAILED_CODE_POST_CONFIRM)

        except Exception as e:
            # logger.error('traceback : %s' % str(traceback.format_exc()))
            if str(e) in [op.FAILED_CODE_FINALIZE, op.FAILED_CODE_GATEWAY_CONNECTION]:
                if exception_msg in op.get_failed_code_choices_dictionary():
                    op.failed_code = op.get_failed_code_choices_dictionary()[exception_msg]
                else:
                    op.failed_cause = exception_msg
                op.status = op.STATUS_FAILED
                op.save()
                op.payment.status = op.payment.STATUS_FAILED
                op.payment.save()
            # elif str(e) == op.FAILED_CODE_GATEWAY_CONNECTION:
            #     pass
            elif str(e) == 'This payment has already been verified.':
                pass
            elif str(e) == op.FAILED_CODE_POST_CONFIRM:
                try:
                    response['post_confirm'] = result.__dict__['__values__']
                    op.response = response
                except:
                    pass
                op.status = op.STATUS_FAILED
                op.failed_code = op.FAILED_CODE_POST_CONFIRM
                op.save()
            else:
                try:
                    response['post_confirm'] = result.__dict__['__values__']
                    op.response = response
                except:
                    pass
                op.status = op.STATUS_FAILED
                op.failed_cause = str(e)
                op.save()

        # client = Client(settings.ZARINPAL['WEBSERVICE_URL'])
        # amount = int(op.payment.total / 10)
        # result = client.service.PaymentVerification(MERCHANT_ID, authority, amount)
        # response['post_confirm'] = result.__dict__['__values__']
        # # result.RefID شماره پیگیری که به تراکنش موفق تخصیص می‌یابد
        # # result.Status
        # if result.Status == 100:
        #     op.ref_id = result.RefID
        #     op.save()
        #     try:
        #         op.finalize(response)
        #     except:
        #         return redirect(
        #             settings.API_BASEURL + reverse('online-payment-report', args=[op.token, 'failed']))
        #     return redirect(settings.API_BASEURL + reverse('online-payment-report', args=[op.token, 'success']))
        #
        # elif result.Status == 101:
        #     op.status = op.STATUS_SUCCESS
        #     op.save()
        #     # Transaction submitted
        #     return redirect(settings.API_BASEURL + reverse('online-payment-report', args=[op.token, 'success']))
        # else:
        #     op.response = response
        #     op.save()
        #     return redirect(settings.API_BASEURL + reverse('online-payment-report', args=[op.token, 'failed']))

    return verification_status
