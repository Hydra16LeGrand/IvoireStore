# Generated by Django 3.1.5 on 2021-03-11 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0004_commande_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='historique',
            name='code_cmd',
            field=models.IntegerField(default=1234567),
            preserve_default=False,
        ),
    ]
