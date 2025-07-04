# Generated by Django 5.2.3 on 2025-06-28 21:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ciudad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(help_text='Nombre descriptivo', max_length=50, verbose_name='Nombre')),
            ],
            options={
                'verbose_name': 'Ciudad',
                'verbose_name_plural': 'Ciudades',
                'ordering': ['nombre'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Direccion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calle', models.CharField(help_text='Nombre de la calle', max_length=50, verbose_name='Calle')),
                ('numero', models.PositiveIntegerField(help_text='Número de la calle', verbose_name='Número')),
                ('ciudad', models.ForeignKey(help_text='Ciudad de la dirección', on_delete=django.db.models.deletion.CASCADE, related_name='direcciones', to='transporte.ciudad', verbose_name='Ciudad')),
            ],
            options={
                'verbose_name': 'Dirección',
                'verbose_name_plural': 'Direcciones',
                'ordering': ['ciudad__nombre', 'calle'],
            },
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(help_text='Nombre del cliente', max_length=50, verbose_name='Nombre')),
                ('apellido', models.CharField(help_text='Apellido del cliente', max_length=50, verbose_name='Apellido')),
                ('telefono', models.CharField(blank=True, help_text='Número de teléfono', max_length=20, null=True, verbose_name='Teléfono')),
                ('nro_documento', models.PositiveBigIntegerField(help_text='Número de documento del cliente', unique=True, verbose_name='Número de documento')),
                ('direccion', models.ForeignKey(help_text='Dirección del cliente', on_delete=django.db.models.deletion.CASCADE, related_name='clientes', to='transporte.direccion', verbose_name='Dirección')),
            ],
            options={
                'verbose_name': 'Cliente',
                'verbose_name_plural': 'Clientes',
                'ordering': ['apellido', 'nombre'],
            },
        ),
        migrations.CreateModel(
            name='Envio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_envio', models.DateTimeField(help_text='Fecha y hora del envío', verbose_name='Fecha de envío')),
                ('estado', models.CharField(choices=[('EN_CAMINO', 'En camino'), ('ENTREGADO', 'Entregado')], default='EN_CAMINO', help_text='Estado actual del envío', max_length=20, verbose_name='Estado')),
                ('cliente', models.ForeignKey(help_text='Cliente que recibe el envío', on_delete=django.db.models.deletion.CASCADE, related_name='envios', to='transporte.cliente', verbose_name='Cliente')),
            ],
            options={
                'verbose_name': 'Envío',
                'verbose_name_plural': 'Envíos',
                'ordering': ['-fecha_envio'],
            },
        ),
        migrations.CreateModel(
            name='Paquete',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('peso', models.DecimalField(decimal_places=2, help_text='Peso del paquete en kg', max_digits=10, verbose_name='Peso')),
                ('ancho', models.DecimalField(decimal_places=2, help_text='Ancho del paquete en cm', max_digits=10, verbose_name='Ancho en cm2')),
                ('alto', models.DecimalField(decimal_places=2, help_text='Alto del paquete en cm', max_digits=10, verbose_name='Alto en cm2')),
                ('longitud', models.DecimalField(decimal_places=2, help_text='Longitud del paquete en cm', max_digits=10, verbose_name='Longitud en cm2')),
                ('descripcion', models.CharField(help_text='Descripción del contenido del paquete', max_length=250, verbose_name='Descripción')),
                ('envio', models.ForeignKey(help_text='Envío al que pertenece el paquete', on_delete=django.db.models.deletion.CASCADE, related_name='paquetes', to='transporte.envio', verbose_name='Envío')),
            ],
            options={
                'verbose_name': 'Paquete',
                'verbose_name_plural': 'Paquetes',
            },
        ),
        migrations.CreateModel(
            name='Provincia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(help_text='Nombre descriptivo', max_length=50, verbose_name='Nombre')),
            ],
            options={
                'verbose_name': 'Provincia',
                'verbose_name_plural': 'Provincias',
                'ordering': ['nombre'],
                'abstract': False,
                'constraints': [models.UniqueConstraint(fields=('nombre',), name='unique_provincia_nombre')],
            },
        ),
        migrations.AddField(
            model_name='ciudad',
            name='provincia',
            field=models.ForeignKey(help_text='Provincia a la que pertenece la ciudad', on_delete=django.db.models.deletion.CASCADE, related_name='ciudades', to='transporte.provincia', verbose_name='Provincia'),
        ),
        migrations.CreateModel(
            name='Sucursal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(help_text='Nombre descriptivo', max_length=50, verbose_name='Nombre')),
                ('direccion', models.ForeignKey(help_text='Dirección de la sucursal', on_delete=django.db.models.deletion.CASCADE, related_name='sucursales', to='transporte.direccion', verbose_name='Dirección')),
            ],
            options={
                'verbose_name': 'Sucursal',
                'verbose_name_plural': 'Sucursales',
                'ordering': ['nombre'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='envio',
            name='sucursal',
            field=models.ForeignKey(help_text='Sucursal desde donde se envía', on_delete=django.db.models.deletion.CASCADE, related_name='envios', to='transporte.sucursal', verbose_name='Sucursal'),
        ),
        migrations.CreateModel(
            name='TipoDocumento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(help_text='Nombre descriptivo', max_length=50, verbose_name='Nombre')),
            ],
            options={
                'verbose_name': 'Tipo de documento',
                'verbose_name_plural': 'Tipos de documento',
                'ordering': ['nombre'],
                'abstract': False,
                'constraints': [models.UniqueConstraint(fields=('nombre',), name='unique_tipo_documento_nombre')],
            },
        ),
        migrations.CreateModel(
            name='Empleado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(help_text='Nombre del empleado', max_length=50, verbose_name='Nombre')),
                ('apellido', models.CharField(help_text='Apellido del empleado', max_length=50, verbose_name='Apellido')),
                ('nro_documento', models.PositiveBigIntegerField(help_text='Número de documento del empleado', unique=True, verbose_name='Número de documento')),
                ('fecha_contratacion', models.DateField(help_text='Fecha en la que fue contratado', verbose_name='Fecha de contratación')),
                ('direccion', models.ForeignKey(help_text='Dirección del empleado', on_delete=django.db.models.deletion.CASCADE, related_name='empleados', to='transporte.direccion', verbose_name='Dirección')),
                ('sucursal', models.ForeignKey(help_text='Sucursal donde trabaja', on_delete=django.db.models.deletion.CASCADE, related_name='empleados', to='transporte.sucursal', verbose_name='Sucursal')),
                ('tipo_documento', models.ForeignKey(help_text='Tipo de documento del empleado', on_delete=django.db.models.deletion.PROTECT, to='transporte.tipodocumento', verbose_name='Tipo de documento')),
            ],
            options={
                'verbose_name': 'Empleado',
                'verbose_name_plural': 'Empleados',
                'ordering': ['apellido', 'nombre'],
            },
        ),
        migrations.AddField(
            model_name='cliente',
            name='tipo_documento',
            field=models.ForeignKey(help_text='Tipo de documento del cliente', on_delete=django.db.models.deletion.PROTECT, to='transporte.tipodocumento', verbose_name='Tipo de documento'),
        ),
        migrations.CreateModel(
            name='TipoVehiculo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(help_text='Nombre descriptivo', max_length=50, verbose_name='Nombre')),
            ],
            options={
                'verbose_name': 'Tipo de vehículo',
                'verbose_name_plural': 'Tipos de vehículo',
                'ordering': ['nombre'],
                'abstract': False,
                'constraints': [models.UniqueConstraint(fields=('nombre',), name='unique_tipo_vehiculo_nombre')],
            },
        ),
        migrations.CreateModel(
            name='Vehiculo',
            fields=[
                ('patente', models.CharField(help_text='Patente del vehículo', max_length=10, primary_key=True, serialize=False, verbose_name='Patente')),
                ('capacidad_carga', models.DecimalField(decimal_places=2, help_text='Capacidad máxima de carga', max_digits=10, verbose_name='Capacidad de carga')),
                ('empleado', models.ForeignKey(help_text='Empleado asignado al vehículo', on_delete=django.db.models.deletion.CASCADE, related_name='vehiculos', to='transporte.empleado', verbose_name='Empleado responsable')),
                ('tipo_vehiculo', models.ForeignKey(help_text='Tipo de vehículo', on_delete=django.db.models.deletion.PROTECT, to='transporte.tipovehiculo', verbose_name='Tipo de vehículo')),
            ],
            options={
                'verbose_name': 'Vehículo',
                'verbose_name_plural': 'Vehículos',
                'ordering': ['patente'],
            },
        ),
        migrations.AddField(
            model_name='envio',
            name='vehiculo',
            field=models.ForeignKey(help_text='Vehículo que realiza el envío', on_delete=django.db.models.deletion.CASCADE, related_name='envios', to='transporte.vehiculo', verbose_name='Vehículo'),
        ),
        migrations.AddConstraint(
            model_name='ciudad',
            constraint=models.UniqueConstraint(fields=('nombre', 'provincia'), name='unique_ciudad_nombre_provincia'),
        ),
        migrations.AddConstraint(
            model_name='sucursal',
            constraint=models.UniqueConstraint(fields=('nombre',), name='unique_sucursal_nombre'),
        ),
        migrations.AddIndex(
            model_name='cliente',
            index=models.Index(fields=['nro_documento'], name='transporte__nro_doc_81d2ab_idx'),
        ),
    ]
