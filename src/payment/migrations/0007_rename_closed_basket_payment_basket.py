# Generated by Django 3.2.12 on 2023-09-29 22:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0006_remove_payment_basket'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='closed_basket',
            new_name='basket',
        ),
    ]
