# Generated by Django 4.2.3 on 2023-10-09 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0015_coupon_delete_copoun'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='status',
            field=models.CharField(choices=[('Active', 'active'), ('Expired', 'expired')], default='Active', max_length=100),
        ),
    ]
