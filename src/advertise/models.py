from django.db import models

from src.users.models import User


class Advertise(models.Model):
    title = models.CharField(max_length=128, verbose_name="عنوان")
    file = models.FileField(upload_to="advertise/", verbose_name="فایل")
    link = models.URLField(verbose_name="لینک")
    is_slider = models.BooleanField(verbose_name="بنر هست / نیست")

    def __str__(self):
        return f"{self.title}({'slider' if self.is_slider else 'not slider'})"

    class Meta:
        verbose_name = "تبلیغات"
        verbose_name_plural = "تبلیغات"


class NewsLetter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="کاربر")
    email = models.EmailField(verbose_name="ایمیل")

    def __str__(self):
        return self.user if self.user else self.email

    class Meta:
        verbose_name = "خبرنامه"
        verbose_name_plural = "خبرنامه"
