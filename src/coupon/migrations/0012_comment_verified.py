# Generated by Django 3.2.12 on 2023-11-14 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0011_remove_category_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='verified',
            field=models.BooleanField(default=False, verbose_name='تایید شده / نشده'),
        ),
    ]
