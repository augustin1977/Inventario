# Generated by Django 5.0.6 on 2024-07-07 01:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Materiais', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='material',
            name='foto1',
            field=models.FileField(upload_to='', verbose_name='Foto do Item'),
        ),
    ]
