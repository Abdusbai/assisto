# Generated by Django 4.1.7 on 2023-07-09 20:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assisto', '0038_delete_pp_alter_acc_user_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='demandes',
            name='demande',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='demandes_set', to='assisto.users'),
        ),
        migrations.AlterField(
            model_name='proofdesc',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='proofdesc_set', to='assisto.demandes'),
        ),
    ]
