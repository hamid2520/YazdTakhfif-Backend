# Generated by Django 3.2.12 on 2023-08-30 00:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basket', '0004_auto_20230829_0355'),
    ]

    operations = [
        migrations.AddField(
            model_name='basketdetail',
            name='final_offer_price',
            field=models.SmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AddField(
            model_name='basketdetail',
            name='final_price',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='basketdetail',
            name='final_price_with_offer',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='basketdetail',
            name='rate',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='basketdetail',
            name='payment_price_with_offer',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
