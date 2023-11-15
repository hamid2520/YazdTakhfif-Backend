# Generated by Django 3.2.12 on 2023-11-14 23:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0011_remove_category_level'),
    ]

    operations = [
        migrations.CreateModel(
            name='CouponImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='coupon_images/', verbose_name='عکس')),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coupon.coupon', verbose_name='کوپن')),
            ],
            options={
                'verbose_name': 'عکس کوپن',
                'verbose_name_plural': 'عکس های کوپن',
            },
        ),
    ]
