# Generated by Django 4.1.7 on 2023-06-03 20:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assisto', '0006_alter_users_commune_alter_users_province'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proofdesc',
            name='proof',
        ),
    ]
