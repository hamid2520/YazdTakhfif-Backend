# Generated by Django 3.2.12 on 2023-08-27 01:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0018_alter_coupon_expire_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='linecoupon',
            name='final_price',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='expire_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2023, 9, 6, 4, 59, 28, 831534)),
        ),
    ]
