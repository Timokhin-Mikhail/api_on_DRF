# Generated by Django 4.1.7 on 2023-04-25 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_order_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderproduct',
            name='date',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='orderproduct',
            name='href',
            field=models.CharField(max_length=200),
        ),
    ]
