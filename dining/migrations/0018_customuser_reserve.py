# Generated by Django 2.1.3 on 2019-02-02 17:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('dining', '0017_auto_20190125_1825'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='reserve',
            field=models.BooleanField(default=True),
        ),
    ]
