# Generated by Django 4.1.7 on 2023-06-10 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assisto', '0012_phoneverification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phoneverification',
            name='phone_date',
            field=models.DateTimeField(),
        ),
    ]
