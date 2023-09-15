# Generated by Django 4.1.7 on 2023-06-14 15:39

import assisto.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assisto', '0015_alter_pp_cin_pdf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='particulier',
            name='cin_pdf',
            field=models.FileField(null=True, upload_to='uploads/', validators=[assisto.validators.validate_file_extension]),
        ),
        migrations.AlterField(
            model_name='pp',
            name='cin_pdf',
            field=models.FileField(null=True, upload_to='uploads/', validators=[assisto.validators.validate_file_extension]),
        ),
    ]
