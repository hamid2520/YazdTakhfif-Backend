# Generated by Django 3.2.12 on 2023-09-28 23:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('basket', '0005_alter_basket_product'),
        ('payment', '0002_alter_payment_basket'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='basket',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='basket.basket'),
        ),
    ]
