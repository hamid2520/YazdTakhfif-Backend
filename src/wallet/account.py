from .models import Account


def get_account_balance(user, datatype):
    commission_obj = Account.objects.filter(owner=user, type=Account.TYPE_COMMISSION).first()
    charge_obj = Account.objects.filter(owner=user, type=Account.TYPE_CHARGE).first()
    if datatype == 'commission':
        if commission_obj:
            return commission_obj.balance
        else:
            return 0
    elif datatype == 'chrage':
        if charge_obj:
            return charge_obj.balance
        else:
            return 0
    else:
        commission_balance = 0
        charge_balance = 0
        if commission_obj:
            commission_balance = commission_obj.balance
        if charge_obj:
            charge_balance = charge_obj.balance
        wallet_balance = commission_balance + charge_balance
        return wallet_balance


def modify_account_balance(user, total_price):
    wallet_balance = get_account_balance(user, 'total')
    commission_balance = get_account_balance(
        user, 'commission')
    charge_balance = get_account_balance(user, 'charge')
    if total_price <= wallet_balance:
        if commission_balance != 0:
            if commission_balance <= total_price:
                total_price -= commission_balance
                Account.objects.filter(
                    owner=user, type=Account.TYPE_COMMISSION).update(balance=0)
                amount_charge = charge_balance - total_price
                total_price = 0
                Account.objects.filter(
                    owner=user, type=Account.TYPE_CHARGE).update(balance=amount_charge)
            else:
                amount_commission = commission_balance - total_price
                total_price = 0
                Account.objects.filter(
                    owner=user, type=Account.TYPE_COMMISSION).update(balance=amount_commission)
        else:
            amount_charge = charge_balance - total_price
            total_price = 0
            Account.objects.filter(
                owner=user, type=Account.TYPE_CHARGE).update(balance=amount_charge)
