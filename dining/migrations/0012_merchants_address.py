# Generated by Django 2.1.3 on 2018-12-28 11:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('dining', '0011_merchants_merchantuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='merchants',
            name='address',
            field=models.CharField(default='', max_length=1000),
        ),
    ]
