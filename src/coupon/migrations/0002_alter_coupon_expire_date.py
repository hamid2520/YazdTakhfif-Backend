# Generated by Django 3.2.12 on 2023-09-06 21:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='expire_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
