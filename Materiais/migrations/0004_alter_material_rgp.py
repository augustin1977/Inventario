# Generated by Django 5.0.6 on 2024-06-27 01:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Materiais', '0003_material_valor_material_valor_currency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='material',
            name='RGP',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
