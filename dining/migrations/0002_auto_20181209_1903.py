# Generated by Django 2.1.3 on 2018-12-09 19:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('dining', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='phone',
            field=models.CharField(max_length=11),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='sex',
            field=models.BooleanField(default=True),
        ),
    ]
