# Generated by Django 4.1.7 on 2023-07-10 21:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assisto', '0043_remove_users_province'),
    ]

    operations = [
        migrations.AddField(
            model_name='particulier',
            name='province',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='assisto.province'),
        ),
    ]
