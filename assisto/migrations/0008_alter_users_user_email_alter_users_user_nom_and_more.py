# Generated by Django 4.1.7 on 2023-06-05 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assisto', '0007_remove_proofdesc_proof'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='user_email',
            field=models.EmailField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='users',
            name='user_nom',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='users',
            name='user_tel',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
