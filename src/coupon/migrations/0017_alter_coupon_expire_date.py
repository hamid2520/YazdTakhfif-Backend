# Generated by Django 3.2.12 on 2023-08-27 01:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0016_auto_20230827_0426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='expire_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2023, 8, 27, 4, 33, 26, 618194)),
        ),
    ]
