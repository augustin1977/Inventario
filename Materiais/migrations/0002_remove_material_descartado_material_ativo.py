# Generated by Django 4.2.13 on 2024-08-21 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Materiais", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="material",
            name="descartado",
        ),
        migrations.AddField(
            model_name="material",
            name="ativo",
            field=models.BooleanField(default=False, verbose_name="ativo"),
        ),
    ]
