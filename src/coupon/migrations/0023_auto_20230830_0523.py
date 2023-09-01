# Generated by Django 3.2.12 on 2023-08-30 01:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0022_alter_coupon_expire_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='linecoupon',
            name='discount_percent',
        ),
        migrations.AddField(
            model_name='linecoupon',
            name='offer_percent',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='coupon',
            name='expire_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2023, 9, 9, 5, 22, 45, 51820)),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='title',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='linecoupon',
            name='final_price',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='linecoupon',
            name='price',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='linecoupon',
            name='title',
            field=models.CharField(max_length=128),
        ),
    ]
