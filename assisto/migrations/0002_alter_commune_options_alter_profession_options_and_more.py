# Generated by Django 4.1.7 on 2023-06-03 20:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assisto', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='commune',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='profession',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='proof',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='province',
            options={'ordering': ['id']},
        ),
        migrations.AlterField(
            model_name='users',
            name='cin_num',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='users',
            name='cnc_num',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='users',
            name='commune',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='assisto.commune'),
        ),
        migrations.AlterField(
            model_name='users',
            name='rc_num',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]
