# Generated by Django 4.1.7 on 2023-04-21 18:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_product_rewiew_sales_specification_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(default=4, on_delete=django.db.models.deletion.PROTECT, related_name='products', to='api.category'),
        ),
    ]
