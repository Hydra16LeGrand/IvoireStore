# Generated by Django 3.1.5 on 2021-03-11 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0003_auto_20210308_1717'),
    ]

    operations = [
        migrations.AddField(
            model_name='commande',
            name='code',
            field=models.IntegerField(default=1928374),
            preserve_default=False,
        ),
    ]
