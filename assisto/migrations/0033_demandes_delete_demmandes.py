# Generated by Django 4.1.7 on 2023-06-26 17:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assisto', '0032_alter_demmandes_demmande'),
    ]

    operations = [
        migrations.CreateModel(
            name='Demandes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True, null=True)),
                ('status', models.BooleanField(blank=True, default=False, null=True)),
                ('message', models.CharField(blank=True, max_length=255, null=True)),
                ('demande', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='demandes_set', to='assisto.proofdesc')),
            ],
        ),
        migrations.DeleteModel(
            name='demmandes',
        ),
    ]