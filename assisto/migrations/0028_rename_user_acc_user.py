# Generated by Django 4.1.7 on 2023-06-22 15:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assisto', '0027_accounttype_user'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='User',
            new_name='Acc_User',
        ),
    ]
