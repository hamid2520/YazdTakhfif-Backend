# Generated by Django 3.2.12 on 2023-09-08 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basket', '0003_alter_basket_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basket',
            name='product',
            field=models.ManyToManyField(blank=True, null=True, to='basket.BasketDetail'),
        ),
    ]
