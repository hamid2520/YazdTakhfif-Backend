# Generated by Django 3.2.12 on 2023-09-10 19:38

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0006_alter_rate_rate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='coupon_rate',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=1, null=True),
        ),
        migrations.AlterField(
            model_name='rate',
            name='rate',
            field=models.SmallIntegerField(validators=[django.core.validators.MaxValueValidator(5)]),
        ),
    ]
