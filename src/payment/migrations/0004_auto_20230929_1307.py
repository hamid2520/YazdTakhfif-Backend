# Generated by Django 3.2.12 on 2023-09-29 09:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('basket', '0005_alter_basket_product'),
        ('payment', '0003_alter_payment_basket'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='closed_basket',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='basket.closedbasket'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='payment',
            name='basket',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='basket.basket'),
        ),
    ]
