# Generated by Django 5.2.4 on 2025-07-04 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transporte', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='direccion',
            constraint=models.UniqueConstraint(fields=('calle', 'numero', 'ciudad'), name='unique_direccion'),
        ),
    ]
