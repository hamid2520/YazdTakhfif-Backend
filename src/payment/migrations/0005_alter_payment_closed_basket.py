# Generated by Django 3.2.12 on 2023-09-29 09:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('basket', '0005_alter_basket_product'),
        ('payment', '0004_auto_20230929_1307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='closed_basket',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='basket.closedbasket'),
        ),
    ]
