# Generated by Django 4.1.7 on 2023-06-26 15:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assisto', '0031_demmandes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='demmandes',
            name='demmande',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='demmandes_set', to='assisto.proofdesc'),
        ),
    ]
