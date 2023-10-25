from rest_framework.response import Response
from rest_framework import status
from rest_framework.serializers import ValidationError
from src.wallet.models import Account, Transaction, Turnover, RequestSettlement
from core.models import UserMeta


def add_request_settlement(user, amount):
    to_acc_change = Account.objects.filter(
        id=Account.ACCOUNT_AZETO_BANK1_ID).first()
    to_acc_commission = Account.objects.filter(
        id=Account.ACCOUNT_AZETO_COMMISSION_ID).first()
    from_acc1 = Account.objects.filter(
        owner=user, type=Account.TYPE_COMMISSION).first()
    from_acc2 = Account.objects.filter(
        owner=user, type=Account.TYPE_CHARGE).first()
    sheba_exist = UserMeta.objects.filter(user=user).first()
    if sheba_exist.shaba:
        balance = from_acc1.balance + from_acc2.balance
        if balance >= 100000:
            if amount:
                if balance >= amount:
                    if from_acc1.balance >= amount:
                        Transaction.add_transaction(
                            from_acc1, to_acc_commission, Transaction.TYPE_WITHDRAW_COMMISSION, amount)
                    else:
                        amount = amount - from_acc1.balance
                        Transaction.add_transaction(
                            from_acc1, to_acc_commission, Transaction.TYPE_WITHDRAW_COMMISSION, from_acc1.balance)

                        Transaction.add_transaction(
                            from_acc2, to_acc_change, Transaction.TYPE_WITHDRAW_COMMISSION, amount)

                    RequestSettlement.objects.create(
                        user=user, amount=amount, status=RequestSettlement.STATUS_UNPAID)
                    return Response({'success': 'درخواست تسویه با موفقیت ثبت شد.'}, status.HTTP_200_OK)
                else:
                    raise ValidationError(
                        {'details': 'مقدار درخواست از موجودی حساب بیشتر است.'})
            else:
                return Response({'details': 'مقدار درخواست وارد نشده است.'}, status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            raise ValidationError(
                {'details': 'موجودی کیف پول شما کمتر از ۱۰۰ هزار تومان است.'})
    else:
        raise ValidationError(
            {'details': 'شماره شبا کاربر در سیستم ثبت نشده است.'})
