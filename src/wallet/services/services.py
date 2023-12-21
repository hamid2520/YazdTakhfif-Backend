# # from core.util.extend import raise_not_field_error
# from src.wallet.models import Account, Transaction
#
#
# def add_user_commission(user, amount):
#     yazd_takhfif_account = Account.objects.filter(id=100)
#     if not yazd_takhfif_account.exists():
#         raise_not_field_error("حساب یزدتخفیف ساخته نشده است !")
#     else:
#         yazd_takhfif_account = yazd_takhfif_account.first()
#
#     user_acc, created = Account.objects.get_or_create(
#         owner=user,
#         type=Account.TYPE_COMMISSION,
#     )
#
#     Transaction.add_transaction(yazd_takhfif_account, user_acc, Transaction.TYPE_DEPOSIT_COMMISSION, amount)
#     return True
