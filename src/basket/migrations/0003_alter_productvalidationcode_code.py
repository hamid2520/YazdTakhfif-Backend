# Generated by Django 3.2.12 on 2023-11-06 16:46

from django.db import migrations, models
import src.basket.models


class Migration(migrations.Migration):

    dependencies = [
        ('basket', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productvalidationcode',
            name='code',
            field=models.CharField(blank=True, db_index=True, default=src.basket.models.generate_random_string, max_length=128, unique=True),
        ),
    ]
