# Generated by Django 3.2.12 on 2023-08-27 01:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0017_alter_coupon_expire_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='expire_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2023, 9, 6, 4, 37, 50, 63295)),
        ),
    ]
