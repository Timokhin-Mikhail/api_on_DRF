# Generated by Django 4.1.7 on 2023-04-21 18:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_rewiew_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='sales',
            name='product',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='sale', to='api.product'),
            preserve_default=False,
        ),
    ]
