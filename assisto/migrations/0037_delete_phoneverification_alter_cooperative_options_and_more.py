# Generated by Django 4.1.7 on 2023-07-06 12:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assisto', '0036_remove_acc_user_acc_type_delete_accounttype'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PhoneVerification',
        ),
        migrations.AlterModelOptions(
            name='cooperative',
            options={'verbose_name_plural': 'Coopérative'},
        ),
        migrations.AlterModelOptions(
            name='particulier',
            options={'verbose_name_plural': 'Particulier'},
        ),
        migrations.AlterModelOptions(
            name='societe',
            options={'verbose_name_plural': 'Société'},
        ),
    ]