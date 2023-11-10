# Generated by Django 3.2.12 on 2023-11-10 17:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.BigIntegerField(default=0, verbose_name='موجودی')),
                ('type', models.SmallIntegerField(choices=[(1, 'حساب پورسانت'), (2, 'حساب شارژ'), (3, 'حساب تسویه')], verbose_name='نوع')),
                ('debit', models.BooleanField(default=False, verbose_name='حساب بدهکاری')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'حساب',
                'verbose_name_plural': 'حساب\u200cها',
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.SmallIntegerField(choices=[(1, 'واریز پورسانت'), (2, 'تسویه پورسانت')], verbose_name='نوع')),
                ('amount', models.BigIntegerField(verbose_name='مبلغ')),
                ('datetime', models.DateTimeField(auto_now_add=True, verbose_name='زمان')),
                ('from_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_account', to='wallet.account', verbose_name='حساب مبدا')),
                ('to_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_account', to='wallet.account', verbose_name='حساب مقصد')),
            ],
            options={
                'verbose_name': 'تراکنش',
                'verbose_name_plural': 'تراکنش\u200cها',
            },
        ),
        migrations.CreateModel(
            name='Turnover',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.BigIntegerField(verbose_name='موجودی')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wallet.account', verbose_name='حساب')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wallet.transaction', verbose_name='تراکنش')),
            ],
            options={
                'verbose_name': 'گردش حساب',
                'verbose_name_plural': 'گردش حساب',
            },
        ),
        migrations.CreateModel(
            name='RequestSettlement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.BigIntegerField(verbose_name='مقدار درخواست')),
                ('status', models.SmallIntegerField(choices=[(1, 'پرداخت نشده'), (2, 'در انتظار تایید'), (3, 'پرداخت شده')], verbose_name='وضعیت پرداخت')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'درخواست تسویه',
                'verbose_name_plural': 'درخواست تسویه',
            },
        ),
    ]
