# Generated by Django 4.1.1 on 2022-10-03 08:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0018_rename_offer_statuspro_products_offerstatuspro'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='products',
            name='offer_product',
        ),
    ]
