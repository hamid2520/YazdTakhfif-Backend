# Generated by Django 3.2.12 on 2023-08-27 00:54

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0014_alter_coupon_expire_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='expire_date',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now),
        ),
    ]
