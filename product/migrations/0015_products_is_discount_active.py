# Generated by Django 4.1.1 on 2022-10-03 04:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0014_products_discount'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='is_discount_active',
            field=models.BooleanField(default=False),
        ),
    ]
