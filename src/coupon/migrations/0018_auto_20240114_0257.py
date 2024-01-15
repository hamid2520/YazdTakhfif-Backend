# Generated by Django 3.2.12 on 2024-01-13 23:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0017_alter_coupon_expire_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='linecoupon',
            name='offer_percent',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='درصد تخفیف'),
        ),
        migrations.AlterField(
            model_name='linecoupon',
            name='price_with_offer',
            field=models.PositiveIntegerField(verbose_name='قیمت با تخفیف'),
        ),
    ]
