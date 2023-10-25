# Generated by Django 3.2.12 on 2023-10-21 15:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('basket', '0014_auto_20231021_1916'),
        ('payment_gateway', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='onlinepayment',
            old_name='datetime',
            new_name='paid_at',
        ),
        migrations.AlterField(
            model_name='onlinepayment',
            name='failed_cause',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='onlinepayment',
            name='payment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='basket.basket'),
        ),
    ]
