# Generated by Django 3.1.5 on 2021-06-26 10:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0007_auto_20210323_1044'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='contact1',
        ),
    ]
