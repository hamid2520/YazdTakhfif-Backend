# Generated by Django 3.2.12 on 2023-08-31 16:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0027_auto_20230830_0547'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='expire_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2023, 9, 10, 20, 10, 34, 388538)),
        ),
    ]
