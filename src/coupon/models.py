import uuid
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import Avg, Count
from django.utils import timezone
from django.utils.text import slugify

# from src.basket.models import ClosedBasket
from src.business.models import Business
from src.users.models import User
from src.utils.generate_random_string import generate_random_code


class Category(models.Model):
    title = models.CharField(max_length=128, unique=True, verbose_name="عنوان")
    slug = models.SlugField(max_length=256, db_index=True, allow_unicode=True, editable=False, blank=True,
                            verbose_name="اسلاگ")
    parent = models.ForeignKey(to="Category", on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name="دسته بندی والد")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.title, allow_unicode=True)
        return super().save(force_insert=False, force_update=False, using=None, update_fields=None)

    def __str__(self):
        return f"{self.title}({'sub' if self.parent else 'main'})"

    class Meta:
        verbose_name = "دسته بندی"
        verbose_name_plural = "دسته بندی ها"


class FAQ(models.Model):
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, verbose_name="دسته بندی")
    title = models.CharField(max_length=1000, verbose_name="عنوان سوال")
    answer = models.CharField(max_length=1000, verbose_name="جواب")

    def __str__(self):
        return f"{self.title[0:15]}({self.category})"

    class Meta:
        verbose_name = "سوالات متداول"
        verbose_name_plural = "سوالات متداول"


class Coupon(models.Model):
    title = models.CharField(max_length=128, verbose_name="عنوان")
    slug = models.SlugField(max_length=256, db_index=True, allow_unicode=True, editable=False, blank=True,
                            verbose_name="اسلاگ")
    business = models.ForeignKey(to=Business, on_delete=models.CASCADE, verbose_name="کسب و کار")
    created = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد کوپن")
    expire_date = models.DateField(null=True, blank=True, verbose_name="تاریخ انقضا")
    active_date = models.DateField(null=True, blank=True, verbose_name="تاریخ فعال سازی")
    is_active = models.BooleanField(default=False, null=True, blank=True, verbose_name='فعال/غیرفعال')
    category = models.ManyToManyField(to=Category, verbose_name="دسته بندی")
    description = models.CharField(max_length=1000, blank=True, null=True, verbose_name="توضیحات")
    terms_of_use = models.TextField(blank=True, null=True, verbose_name="شرایط استفاده")
    coupon_rate = models.DecimalField(default=0, blank=True, max_digits=2, decimal_places=1, verbose_name="امتیاز کوپن")
    rate_count = models.PositiveIntegerField(default=0, blank=True, verbose_name="تعداد رای دهندگان")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
            while Coupon.objects.exclude(id=self.id).filter(slug=self.slug).exists():
                self.slug += generate_random_code()
        if not self.expire_date:
            self.expire_date = timezone.now() + timedelta(days=10)
        if not self.active_date:
            self.active_date = timezone.now()
        return super().save(force_insert, force_update, using, update_fields)

    def get_main_line_coupon(self):
        return self.linecoupon_set.filter(is_main=True).first()

    def __str__(self):
        return f"{self.title}({self.business})"

    class Meta:
        verbose_name = "کوپن"
        verbose_name_plural = "کوپن ها"


class CouponImage(models.Model):
    image = models.ImageField(upload_to="coupon_images/", verbose_name="عکس")
    coupon = models.ForeignKey(to=Coupon, on_delete=models.CASCADE, verbose_name="کوپن")

    def __str__(self):
        return f"{self.coupon.title}({self.id})"

    class Meta:
        verbose_name = "عکس کوپن"
        verbose_name_plural = "عکس های کوپن"


class LineCoupon(models.Model):
    slug = models.SlugField(db_index=True, blank=True, null=True, editable=False, unique=True, verbose_name="اسلاگ")
    title = models.CharField(max_length=128, verbose_name="عنوان")
    coupon = models.ForeignKey(to=Coupon, on_delete=models.CASCADE, verbose_name="کوپن")
    is_main = models.BooleanField(default=False, verbose_name="اصلی هست / نیست",
                                  help_text="در هر کوپن فقط 1 لاین میتواند اصلی باشد!")
    count = models.PositiveIntegerField(verbose_name="تعداد")
    price = models.PositiveIntegerField(verbose_name="قیمت")
    offer_percent = models.PositiveSmallIntegerField(blank=True, default=0, verbose_name="درصد تخفیف")
    price_with_offer = models.PositiveIntegerField(verbose_name="قیمت با تخفیف")
    sell_count = models.PositiveIntegerField(blank=True, default=0, verbose_name="تعداد فروخته شده")
    commission = models.PositiveIntegerField(default=0, verbose_name="پورسانت")

    def validate_unique(self, exclude=None):
        if self.is_main:
            lines = LineCoupon.objects.filter(coupon__id=self.coupon.id, is_main=True)
            if lines.exists():
                if not lines.first().id == self.id:
                    raise ValidationError({"is_main": "فقط یک لاین کوپن می تواند اصلی باشد!"})
        return super().validate_unique(exclude)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.slug is None:
            self.slug = f"{self.__class__.__name__.lower()}-{uuid.uuid4()}"
        self.offer_percent = ((self.price - self.price_with_offer) / self.price) * 100
        self.full_clean(exclude=None, validate_unique=True)
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f"{self.coupon}({self.title})"

    class Meta:
        verbose_name = "لاین کوپن"
        verbose_name_plural = "لاین کوپن ها"


class Rate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, verbose_name="کوپن")
    rate = models.PositiveSmallIntegerField(validators=[MaxValueValidator(5), ], verbose_name="امتیاز",
                                            help_text="امتیاز باید بین 1 تا 5 و بصورت عدد صحیح باشد!")

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        detail = self.coupon.rate_set.all().aggregate(Avg("rate"), Count("id"))
        self.coupon.coupon_rate = detail["rate__avg"]
        self.coupon.rate_count = detail["id__count"]
        self.coupon.save()
        return super().save(force_insert, force_update, using,
                            update_fields)

    def __str__(self):
        return f"{self.coupon.title}({self.user.username})"

    class Meta:
        verbose_name = "بازخورد"
        verbose_name_plural = "بازخوردها"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    parent = models.ForeignKey("Comment", on_delete=models.CASCADE, blank=True, null=True)
    text = models.CharField(max_length=1200)
    created_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False, verbose_name="تایید شده / نشده")

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "نظر"
        verbose_name_plural = "نظرات"
