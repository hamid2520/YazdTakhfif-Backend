# Generated by Django 3.2.12 on 2023-11-13 15:24

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0004_auto_20231113_1854'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('coupon', '0011_remove_category_level'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'دسته بندی', 'verbose_name_plural': 'دسته بندی ها'},
        ),
        migrations.AlterModelOptions(
            name='comment',
            options={'verbose_name': 'نظر', 'verbose_name_plural': 'نظرات'},
        ),
        migrations.AlterModelOptions(
            name='coupon',
            options={'verbose_name': 'کوپن', 'verbose_name_plural': 'کوپن ها'},
        ),
        migrations.AlterModelOptions(
            name='faq',
            options={'verbose_name': 'سوالات متداول', 'verbose_name_plural': 'سوالات متداول'},
        ),
        migrations.AlterModelOptions(
            name='linecoupon',
            options={'verbose_name': 'لاین کوپن', 'verbose_name_plural': 'لاین کوپن ها'},
        ),
        migrations.AlterModelOptions(
            name='rate',
            options={'verbose_name': 'بازخورد', 'verbose_name_plural': 'بازخوردها'},
        ),
        migrations.AlterField(
            model_name='category',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coupon.category', verbose_name='دسته بندی والد'),
        ),
        migrations.AlterField(
            model_name='category',
            name='title',
            field=models.CharField(max_length=128, unique=True, verbose_name='عنوان'),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='business.business', verbose_name='کسب و کار'),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='category',
            field=models.ManyToManyField(to='coupon.Category', verbose_name='دسته بندی'),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='coupon_rate',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=2, null=True, verbose_name='امتیاز کوپن'),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد کوپن'),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='description',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='توضیحات'),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='expire_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='تاریخ انقضا'),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='rate_count',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='تعداد رای دهندگان'),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='terms_of_use',
            field=models.TextField(blank=True, null=True, verbose_name='شرایط استفاده'),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='title',
            field=models.CharField(max_length=128, verbose_name='عنوان'),
        ),
        migrations.AlterField(
            model_name='faq',
            name='answer',
            field=models.CharField(max_length=1000, verbose_name='جواب'),
        ),
        migrations.AlterField(
            model_name='faq',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coupon.category', verbose_name='دسته بندی'),
        ),
        migrations.AlterField(
            model_name='faq',
            name='title',
            field=models.CharField(max_length=1000, verbose_name='عنوان سوال'),
        ),
        migrations.AlterField(
            model_name='linecoupon',
            name='count',
            field=models.PositiveIntegerField(verbose_name='تعداد'),
        ),
        migrations.AlterField(
            model_name='linecoupon',
            name='coupon',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coupon.coupon', verbose_name='کوپن'),
        ),
        migrations.AlterField(
            model_name='linecoupon',
            name='is_main',
            field=models.BooleanField(default=False, help_text='در هر کوپن فقط 1 لاین میتواند اصلی باشد!', verbose_name='اصلی هست / نیست'),
        ),
        migrations.AlterField(
            model_name='linecoupon',
            name='offer_percent',
            field=models.PositiveSmallIntegerField(verbose_name='درصد تخفیف'),
        ),
        migrations.AlterField(
            model_name='linecoupon',
            name='price',
            field=models.PositiveIntegerField(verbose_name='قیمت'),
        ),
        migrations.AlterField(
            model_name='linecoupon',
            name='price_with_offer',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='قیمت با تخفیف'),
        ),
        migrations.AlterField(
            model_name='linecoupon',
            name='sell_count',
            field=models.PositiveIntegerField(blank=True, default=0, verbose_name='تعداد فروخته شده'),
        ),
        migrations.AlterField(
            model_name='linecoupon',
            name='title',
            field=models.CharField(max_length=128, verbose_name='عنوان'),
        ),
        migrations.AlterField(
            model_name='rate',
            name='coupon',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coupon.coupon', verbose_name='کوپن'),
        ),
        migrations.AlterField(
            model_name='rate',
            name='rate',
            field=models.PositiveSmallIntegerField(help_text='امتیاز باید بین 1 تا 5 و بصورت عدد صحیح باشد!', validators=[django.core.validators.MaxValueValidator(5)], verbose_name='امتیاز'),
        ),
        migrations.AlterField(
            model_name='rate',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
        ),
    ]
