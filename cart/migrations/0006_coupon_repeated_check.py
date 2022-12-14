# Generated by Django 4.1.1 on 2022-10-02 19:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cart', '0005_alter_coupon_coupon_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='coupon_repeated_check',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_repeated', models.BooleanField(default=False)),
                ('coupon_name', models.CharField(max_length=100, null=True)),
                ('user_name', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
