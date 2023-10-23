#
# az-iranian-bank-gateways==1.6.15
#
# class Gateway(TrackModel):
#     class Meta:
#         verbose_name = 'درگاه'
#         verbose_name_plural = 'درگاه‌ها'
#
#     CODE_ZARINPAL = 1
#     CODE_OTHER = 1
#
#     CODE_CHOICES = (
#         (CODE_ZARINPAL, 'زرین پال'),
#         (CODE_OTHER, 'درگاه های دیگر'),
#     )
#
#     ZARINPAL_STATUS_CODES = {
#         -1: 'اطلاعات ارسال شده ناقص است.',
#         -2: 'IP و یا مرچنت کد پذیرنده صحیح نیست',
#         -3: 'با توجه به محدودیت های شاپرک امکان پرداخت با رقم درخواست شده میسر نمی باشد.',
#         -4: 'سطح تایید پذیرنده پایین تر از سطح نقره ای است.',
#         -11: 'درخواست مورد نظر یافت نشد.',
#         -12: 'امکان ویرایش درخواست میسر نمی باشد.',
#         -21: 'هیچ نوع عملیات مالی برای این تراکنش یافت نشد.',
#         -22: 'تراکنش ناموفق می‌باشد.',
#         -33: 'رقم تراکنش با رقم پرداخت شده مطابقت ندارد.',
#         -34: 'سقف تقسیم تراکنش از لحاظ تعداد یا رقم عبور نموده است',
#         -40: 'اجازه دسترسی به متد مربوطه وجود ندارد.',
#         -41: 'اطلاعات ارسال شده مربوط به AdditionalData غیرمعتبر می‌باشد.',
#         -42: 'مدت زمان معتبر طول عمر شناسه پرداخت باید بین ۳۰ دقیقه تا ۴۵ روز می باشد.',
#         -54: 'درخواست مورد نظر آرشیو شده است.',
#         100: 'عملیات با موفقیت انجام گردیده است.',
#         101: 'عملیات پرداخت موفق بوده و قبلا PaymentVerification تراکنش انجام شده است.',
#     }
#
#     code = models.PositiveSmallIntegerField(choices=CODE_CHOICES)
#     # put merchant_id or any thing else in data
#     data = models.JSONField(default=dict, null=True, blank=True)
#     active = models.BooleanField(default=True)
#     logo = models.CharField(max_length=256, blank=True,
#                             null=True, default='', verbose_name='لوگو')
#
#
# class OnlinePayment(TrackModel):
#     class Meta:
#         verbose_name = 'پرداخت آنلاین'
#         verbose_name_plural = 'پرداخت آنلاین'
#
#     STATUS_NEW = 1
#     STATUS_PENDING = 2
#     STATUS_SUCCESS = 3
#     STATUS_FAILED = 4
#     STATUS_CANCEL = 5
#     STATUS_CHOICES = (
#         (STATUS_NEW, 'جدید'),
#         (STATUS_PENDING, 'انتظار'),
#         (STATUS_SUCCESS, 'موفق'),
#         (STATUS_FAILED, 'ناموفق'),
#         (STATUS_CANCEL, 'لغو'),
#     )
#
#     FAILED_CODE_NO_ERROR = 'بدون خطا'
#     FAILED_CODE_GOTO_GATEWAY = 'خطای انتقال به درگاه پرداخت'
#     FAILED_CODE_PRE_CONFIRM = 'خطای پرداخت در درگاه'
#     FAILED_CODE_POST_CONFIRM = 'خطای اعتبار سنجی پرداخت'
#     FAILED_CODE_GATEWAY_CONNECTION = 'خطای ارتباط با درگاه پرداخت'
#     FAILED_CODE_FINALIZE = 'خطای نهایی سازی پرداخت'
#     FAILED_CODE_CHOICES = (
#         (0, FAILED_CODE_NO_ERROR),
#         (5, FAILED_CODE_GOTO_GATEWAY),
#         (10, FAILED_CODE_PRE_CONFIRM),
#         (15, FAILED_CODE_POST_CONFIRM),
#         (20, FAILED_CODE_GATEWAY_CONNECTION),
#         (30, FAILED_CODE_FINALIZE),
#     )
#
#     user = models.ForeignKey(User, on_delete=models.PROTECT)
#     status = models.PositiveSmallIntegerField(
#         default=STATUS_NEW, verbose_name='وضعیت', choices=STATUS_CHOICES)
#     token = models.UUIDField(
#         default=uuid.uuid4, editable=False, unique=True, verbose_name='توکن')
#     gateway = models.ForeignKey(Gateway, on_delete=models.CASCADE)
#     # جواب هنگام ارسال به درگاه پرداخت
#     extra_data = models.JSONField(default=dict, null=True, blank=True)
#     # جواب بعد پرداخت
#     # {pre_confirm={}, post_confirm={}}
#     response = models.JSONField(default=dict, null=True, blank=True)
#     ref_id = models.CharField(
#         max_length=64, blank=True, null=True, default=None)
#     payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
#     # زمان نهایی شدن پرداخت
#     datetime = models.DateTimeField(null=True, blank=True, default=None)
#     # endpoint = models.PositiveSmallIntegerField(choices=ENDPOINT_CHOICES)
#     failed_code = models.IntegerField(default=0, choices=FAILED_CODE_CHOICES)
#     failed_cause = models.CharField(max_length=255, default='')
#
#     def __str__(self):
#         return str(self.token)
#
#     # def __str__(self):
#     #     return '{} - {}'.format(self.member.user.get_full_name(), self.user.lender.name)
#
#     def finalize(self):
#         self.payment.finalize()
#         self.status = self.STATUS_SUCCESS
#         # self.created_at = datetime.datetime.now()
#         self.save()
#         return self.payment
#
#     @staticmethod
#     def get_failed_code_choices_dictionary():
#         return {v: k for k, v in OnlinePayment.FAILED_CODE_CHOICES}
#
#     def goto_gateway(self):
#         if self.gateway.code == Gateway.CODE_ZARINPAL:
#             from .util.ipg import zarinpal
#             return zarinpal.goto_gateway(self)
#         else:
#             return False, self
#
#     def verify_payment(self, request):
#         if self.gateway.code == Gateway.CODE_ZARINPAL:
#             from .util.ipg import zarinpal
#             return zarinpal.verify_payment(self, request)
#         else:
#             return False
#
#     def get_redirect_url(self):
#         if self.payment.education:
#             return settings.REDIRECT_URL['EDUCATION_URL']
#         return settings.REDIRECT_URL['USER_URL']
#
#
#
# def go_to_gateway_view_v2(request, token):
#     op = OnlinePayment.objects.filter(token=token).first()
#     if not op or op.status not in [op.STATUS_NEW]:
#         return redirect(settings.API_BASEURL + reverse('online-payment-report-v2', args=[token, 'failed']))
#     # خواندن مبلغ از هر جایی که مد نظر است
#     amount = int(op.payment.total)
#     # تنظیم شماره موبایل کاربر از هر جایی که مد نظر است
#     user_mobile_number = op.user.usermeta.phone  # اختیاری
#     client_callback_url = settings.API_BASEURL + \
#                           reverse('callback-gateway-v2', args=[token])
#     factory = bankfactories.BankFactory()
#     try:
#         bank = factory.create()  # or factory.create(bank_models.BankType.BMI) or set identifier
#         bank.set_request(request)
#         bank.set_amount(amount)
#         # یو آر ال بازگشت به نرم افزار برای ادامه فرآیند
#         bank.set_client_callback_url(client_callback_url)
#         bank.set_mobile_number(user_mobile_number)  # اختیاری
#
#         # در صورت تمایل اتصال این رکورد به رکورد فاکتور یا هر چیزی که بعدا بتوانید ارتباط بین محصول یا خدمات را با این
#         # پرداخت برقرار کنید.
#         bank_record = bank.ready()
#
#         # هدایت کاربر به درگاه بانک
#         return bank.redirect_gateway()
#     except AZBankGatewaysException as e:
#         logging.critical(e)
#         # TODO: redirect to failed page.
#         raise e
#
#
#
# def callback_gateway_view_v2(request, token):
#     op = OnlinePayment.objects.filter(token=token).first()
#     tracking_code = request.GET.get(
#         azbankgateways_settings.TRACKING_CODE_QUERY_PARAM, None)
#     if not tracking_code:
#         logging.debug("این لینک معتبر نیست.")
#         raise Http404
#
#     try:
#         bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
#     except bank_models.Bank.DoesNotExist:
#         logging.debug("این لینک معتبر نیست.")
#         raise Http404
#
#     # در این قسمت باید از طریق داده هایی که در بانک رکورد وجود دارد، رکورد متناظر یا هر اقدام مقتضی دیگر را انجام دهیم
#     if bank_record.is_success:
#         response = {"pre_confirm": {"Status": "OK", "Authority": ""}, "post_confirm": {
#             "RefID": bank_record.reference_number, "Status": bank_record.status}}
#         op.response = response
#         op.status = OnlinePayment.STATUS_SUCCESS
#         op.save()
#         if op.payment.payment_type == Payment.TYPE_CHARGE:
#             new_balance = op.payment.total
#             to_data = Account.objects.filter(
#                 owner=op.user, type=Account.TYPE_CHARGE).first()
#             from_data = Account.objects.filter(id=101).first()
#             if not to_data:
#                 to_data = Account.objects.create(
#                     balance=0, type=Account.TYPE_CHARGE, owner=op.user)
#             Transaction.add_transaction(
#                 from_data, to_data, Account.TYPE_CHARGE, new_balance)
#             pay_last = op.payment.finalize_after_charge
#             if pay_last:
#                 if account.get_account_balance(op.user, 'total') >= pay_last.total:
#                     account.modify_account_balance(
#                         op.user, pay_last.total)
#                     pay_last.finalize()
#                     op.payment.finalize_charge()
#                 else:
#                     op.payment.finalize_charge()
#                     Payment.objects.filter(pk=op.payment.finalize_after_charge.id).update(
#                         status=Payment.STATUS_FAILED)
#                     op.status = OnlinePayment.STATUS_FAILED
#                     response = {"pre_confirm": {"Status": bank_record.is_success, "Authority": ""}, "post_confirm": {
#                         "RefID": bank_record.reference_number, "Status": bank_record.status}}
#                     op.response = response
#                     op.save()
#                     Campaign.send_template_sms(
#                         to=op.user.usermeta.phone,
#                         tpl='failPayment',
#                         context={
#                             'token': op.user.first_name + " " + "عزیز",
#                             'token2': op.payment.id,
#                         },
#                         priority=Campaign.PRIORITY_CRITICAL
#                     )
#                     Message = apps.get_model('notification', 'Message')
#                     Message.objects.create(recipient_user=op.user, is_read=False,
#                                            title="پرداخت ناموفق", content=op.payment.id)
#                     return redirect(settings.API_BASEURL + reverse('online-payment-report-v2', args=[token, 'failed']))
#             else:
#                 try:
#                     op.payment.finalize_charge()
#                 except Exception as e:
#                     raise Exception(op.FAILED_CODE_FINALIZE)
#         else:
#             try:
#                 op.payment.finalize_charge()
#             except Exception as e:
#                 raise Exception(op.FAILED_CODE_FINALIZE)
#
#         Campaign.send_template_sms(
#             to=op.user.usermeta.phone,
#             tpl='successfulPayment',
#             context={
#                 'token': op.user.first_name + " " + "عزیز",
#                 'token2': op.payment.id,
#             },
#             priority=Campaign.PRIORITY_CRITICAL
#         )
#         Message = apps.get_model('notification', 'Message')
#         Message.objects.create(
#             recipient_user=op.user, is_read=False, title="پرداخت موفق", content=op.payment.id)
#
#         return redirect(settings.API_BASEURL + reverse(
#             'online-payment-report-v2',
#             args=[op.token, 'success']))
#
#     op.status = OnlinePayment.STATUS_FAILED
#     response = {"pre_confirm": {"Status": bank_record.is_success, "Authority": ""}, "post_confirm": {
#         "RefID": bank_record.reference_number, "Status": bank_record.status}}
#     op.response = response
#     op.save()
#     Campaign.send_template_sms(
#         to=op.user.usermeta.phone,
#         tpl='failPayment',
#         context={
#             'token': op.user.first_name + " " + "عزیز",
#             'token2': op.payment.id,
#         },
#         priority=Campaign.PRIORITY_CRITICAL
#     )
#     Message = apps.get_model('notification', 'Message')
#     Message.objects.create(recipient_user=op.user, is_read=False,
#                            title="پرداخت ناموفق", content=op.payment.id)
#     # پرداخت موفق نبوده است. اگر پول کم شده است ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت.
#     # return HttpResponse("پرداخت با شکست مواجه شده است. اگر پول کم شده است ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت.")
#     return redirect(settings.API_BASEURL + reverse('online-payment-report-v2', args=[token, 'failed']))
