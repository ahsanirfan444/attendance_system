# Generated by Django 3.0.2 on 2022-07-27 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance_api', '0010_auto_20220727_1313'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='radius',
            field=models.IntegerField(default=0),
        ),
    ]
