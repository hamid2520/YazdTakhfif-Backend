# Generated by Django 3.2.12 on 2023-09-01 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basket', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basketdetail',
            name='count',
            field=models.PositiveSmallIntegerField(),
        ),
    ]
