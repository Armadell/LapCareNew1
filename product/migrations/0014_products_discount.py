# Generated by Django 4.1.1 on 2022-10-02 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0013_remove_banner_is_active_remove_banner_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='discount',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
