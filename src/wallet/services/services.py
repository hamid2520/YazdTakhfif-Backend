from core.util.extend import raise_not_field_error
from src.wallet.models import Account, Transaction


def add_user_commission(user, amount):
    azeto_account = Account.objects.filter(id=100)
    if not azeto_account.exists():
        raise_not_field_error("حساب آزتو ساخته نشده است !")
    else:
        azeto_account = azeto_account.first()

    user_acc, created = Account.objects.get_or_create(
        owner=user,
        type=Account.TYPE_COMMISSION,
    )

    Transaction.add_transaction(azeto_account, user_acc, Transaction.TYPE_DEPOSIT_COMMISSION, amount)
    return True
