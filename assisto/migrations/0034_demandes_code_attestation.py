# Generated by Django 4.1.7 on 2023-07-05 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assisto', '0033_demandes_delete_demmandes'),
    ]

    operations = [
        migrations.AddField(
            model_name='demandes',
            name='code_attestation',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
