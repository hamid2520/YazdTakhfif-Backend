# Generated by Django 3.2.12 on 2023-07-12 22:14

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0005_coupon_expire_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='expire_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 12, 22, 14, 9, 63947, tzinfo=utc)),
        ),
    ]
