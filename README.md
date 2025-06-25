# Tutorial: Despliegue de una Aplicación Django con Docker
Práctico de Mapeo Objeto-Relacional para la materia, Bases de Datos de la carrera `Ingeniería en Sistemas` de la *`Universidad Tecnológica Nacional`* *`Facultad Regional Villa María`*.

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Django 5.1.11](https://img.shields.io/badge/Django%205.1.11-092E20?style=for-the-badge&logo=django&logoColor=white)
![Alpine Linux](https://img.shields.io/badge/Alpine_Linux-0D597F?style=for-the-badge&logo=alpine-linux&logoColor=white)
![Python 3.13](https://img.shields.io/badge/Python%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL 17](https://img.shields.io/badge/PostgreSQL%2017-336791?style=for-the-badge&logo=postgresql&logoColor=white)

**Referencia Rápida**

**Mantenido Por:** Grupo 8

## **Descargo de Responsabilidad:**
El código proporcionado se ofrece "tal cual", sin garantía de ningún tipo, expresa o implícita. En ningún caso los autores o titulares de derechos de autor serán responsables de cualquier reclamo, daño u otra responsabilidad.


## Introducción
Este tutorial te guiará paso a paso en la creación y despliegue de una aplicación Django utilizando Docker y Docker Compose. El objetivo es que puedas levantar un entorno de desarrollo profesional, portable y fácil de mantener, ideal tanto para pruebas como para producción.

---

## Requisitos Previos
- **Docker** y **Docker Compose** instalados en tu sistema. Puedes consultar la [documentación oficial de Docker](https://docs.docker.com/get-docker/) para la instalación.
- Conocimientos básicos de Python y Django (no excluyente, el tutorial es autoexplicativo).

### Recursos Útiles
- [Tutorial oficial de Django](https://docs.djangoproject.com/en/2.0/intro/tutorial01/)
- [Cómo crear un entorno virtual en Python](https://docs.djangoproject.com/en/2.0/intro/contributing/)

---

## 1. Estructura del Proyecto
Crea una carpeta para tu proyecto. En este ejemplo, la llamaremos `transporte`.

> **Puedes copiar todo este bloque y pegarlo directamente en tu terminal o archivo correspondiente.**
```sh
mkdir transporte
cd transporte/
```

---

## 2. Definición de Dependencias
Crea un archivo `requirements.txt` para listar las dependencias de Python necesarias para tu aplicación.

> **Puedes copiar todo este bloque y pegarlo directamente en tu archivo requirements.txt.**
```txt
# requirements.txt
Django
psycopg[binary]  # Driver para PostgreSQL
```

---

## 3. Creación del Dockerfile
El `Dockerfile` define la imagen de Docker que contendrá tu aplicación. Aquí se detallan las etapas de construcción, instalación de dependencias y configuración del entorno.

> **Puedes copiar todo este bloque y pegarlo directamente en tu archivo Dockerfile.**
```dockerfile
# Etapa de construcción
FROM python:3.13-alpine AS base
LABEL maintainer="Grupo 8"
LABEL version="1.0"
LABEL description="cloudset"
RUN apk --no-cache add bash pango ttf-freefont py3-pip curl

# Etapa de construcción
FROM base AS builder
# Instalación de dependencias de construcción
RUN apk --no-cache add py3-pip py3-pillow py3-brotli py3-scipy py3-cffi \
  linux-headers autoconf automake libtool gcc cmake python3-dev \
  fortify-headers binutils libffi-dev wget openssl-dev libc-dev \
  g++ make musl-dev pkgconf libpng-dev openblas-dev build-base \
  font-noto terminus-font libffi

# Copia solo los archivos necesarios para instalar dependencias de Python
COPY ./requirements.txt .

# Instalación de dependencias de Python
RUN pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt \
  && rm requirements.txt

# Etapa de producción
FROM base
RUN mkdir /code
WORKDIR /code
# Copia solo los archivos necesarios desde la etapa de construcción
COPY ./requirements.txt .
RUN pip install -r requirements.txt \
  && rm requirements.txt
COPY --chown=user:group --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.12/site-packages 
#COPY --from=build-python /usr/local/bin/ /usr/local/bin/
ENV PATH /usr/local/lib/python3.13/site-packages:$PATH
# Configuración adicional
RUN ln -s /usr/share/zoneinfo/America/Cordoba /etc/localtime

# Comando predeterminado
CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "app.wsgi"]

```

---

## 4. Configuración de Variables de Entorno
Crea un archivo `.env.db` para almacenar las variables de entorno necesarias para la conexión a la base de datos.

> **Puedes copiar todo este bloque y pegarlo directamente en tu archivo .env.db.**
```conf
# .env.db
# .env.db
DATABASE_ENGINE=django.db.backends.postgresql
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=postgres
POSTGRES_USER=postgres
PGUSER=${POSTGRES_USER}
POSTGRES_PASSWORD=postgres
LANG=es_AR.utf8
POSTGRES_INITDB_ARGS="--locale-provider=icu --icu-locale=es-AR --auth-local=trust"
```

---

## 5. Definición de Servicios con Docker Compose
El archivo `docker-compose.yml` orquesta los servicios necesarios: base de datos, backend de Django y utilidades para generación y administración del proyecto.

> **Puedes copiar todo este bloque y pegarlo directamente en tu archivo docker-compose.yml.**
```yml
services:
  db:
    image: postgres:alpine
    env_file:
      - .env.db
    environment:
      - POSTGRES_INITDB_ARGS=--auth-host=md5 --auth-local=trust
    healthcheck:
      test: [ "CMD-SHELL", "pg_isready" ]
      interval: 10s
      timeout: 2s
      retries: 5
    volumes:
      - postgres-db:/var/lib/postgresql/data
    networks:
      - net

  backend:
    build: .
    command: runserver 0.0.0.0:8000
    entrypoint: python3 manage.py
    env_file:
      - .env.db
    expose:
      - "8000"
    ports:
      - "8000:8000"
    volumes:
      - ./src:/code
    depends_on:
      db:
        condition: service_healthy
    networks:
      - net

  generate:
    build: .
    user: root
    command: /bin/sh -c 'mkdir src && django-admin startproject app src'
    env_file:
      - .env.db
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - .:/code
    networks:
      - net

  manage:
    build: .
    entrypoint: python3 manage.py
    env_file:
      - .env.db
    volumes:
      - ./src:/code
    depends_on:
      db:
        condition: service_healthy
    networks:
      - net

networks:
  net:

volumes:
  postgres-db:
```

---

## 6. Generación y Configuración de la Aplicación

### Generar la estructura base del proyecto y la app

Hay que tener el archivo `LICENSE` para que la generación de la imagen no produzca un error.
> **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
```sh
docker compose run --rm generate
docker compose run --rm manage startapp transporte
sudo chown $USER:$USER -R .
```

### Configuración de `settings.py`
Edita el archivo `settings.py` para agregar tu app y configurar la base de datos usando las variables de entorno.

> **Puedes copiar todo este bloque y pegarlo al final directamente en tu archivo ./src/app/settings.py.**
```python
import os

ALLOWED_HOSTS = [os.environ.get("ALLOWED_HOSTS", "*")]

INSTALLED_APPS += [
    'transporte',
]

# Configuración condicional de base de datos
USE_POSTGRES = os.environ.get("USE_POSTGRES", "").lower() == "true"

if USE_POSTGRES:
    DATABASES = {
        "default": {
            "ENGINE": os.environ.get("DATABASE_ENGINE", "django.db.backends.postgresql"),
            "NAME": os.environ.get("POSTGRES_DB", ""),
            "USER": os.environ.get("POSTGRES_USER", ""),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
            "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }
else:
    # Base de datos por defecto (SQLite)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

---

## 7. Primeros Pasos con Django

### Migrar la base de datos
> **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
```sh
docker compose run --rm manage migrate
```

### Crear un superusuario
> **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
```sh
docker compose run --rm manage createsuperuser
```

### Iniciar la aplicación
> **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
```sh
docker compose up -d backend
```
Accede a la administración de Django en [http://localhost:8000/admin/](http://localhost:8000/admin/)

### Ver logs de los contenedores
> **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
```sh
docker compose logs -f
```

---

## 8. Comandos Útiles
- **Aplicar migraciones:**
  > **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
  ```sh
  docker compose run manage makemigrations
  docker compose run manage migrate
  ```
- **Detener y eliminar contenedores:**
  > **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
  ```sh
  docker compose down
  ```
- **Detener y eliminar contenedores con imagenes y contenedores sin uso:**
  > **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
  ```sh
  docker compose down -v --remove-orphans --rmi all
  ```
- **Limpiar recursos de Docker:**
  > **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
  ```sh
  docker system prune -a
  ```
- **Cambiar permisos de archivos:**
  > **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
  ```sh
  sudo chown $USER:$USER -R .
  ```

---

## 9. Modelado de la Aplicación

### Ejemplo de `models.py`
Incluye modelos bien documentados y estructurados para una gestión profesional de tus datos.

> **Puedes copiar todo este bloque y pegarlo directamente en tu archivo ./src/pastas/models.py.**
```python
from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from datetime import date


class NombreAbstract(models.Model):
    nombre = models.CharField(
        _('Nombre'),
        max_length=50,
        help_text=_('Nombre descriptivo'),
    )

    def save(self, *args, **kwargs):
        if self.nombre:
            self.nombre = self.nombre.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    class Meta:
        abstract = True
        ordering = ['nombre']


class Provincia(NombreAbstract):
    class Meta:
        verbose_name = _('Provincia')
        verbose_name_plural = _('Provincias')


class Ciudad(NombreAbstract):
    provincia = models.ForeignKey(
        Provincia,
        on_delete=models.CASCADE,
        related_name='ciudades',
        verbose_name=_('Provincia'),
        help_text=_('Provincia a la que pertenece la ciudad'),
    )

    def __str__(self):
        return f"{self.nombre} ({self.provincia.nombre})"

    class Meta:
        verbose_name = _('Ciudad')
        verbose_name_plural = _('Ciudades')


class Direccion(models.Model):
    calle = models.CharField(
        _('Calle'),
        max_length=50,
        help_text=_('Nombre de la calle'),
    )
    numero = models.PositiveIntegerField(
        _('Número'),
        help_text=_('Número de la calle'),
    )
    ciudad = models.ForeignKey(
        Ciudad,
        on_delete=models.CASCADE,
        related_name='direcciones',
        verbose_name=_('Ciudad'),
        help_text=_('Ciudad de la dirección'),
    )

    def __str__(self):
        return f"{self.calle} {self.numero}, {self.ciudad.nombre}"

    class Meta:
        verbose_name = _('Dirección')
        verbose_name_plural = _('Direcciones')
        ordering = ['ciudad__nombre', 'calle']


class TipoDocumento(NombreAbstract):
    class Meta:
        verbose_name = _('Tipo de documento')
        verbose_name_plural = _('Tipos de documento')


class Sucursal(NombreAbstract):
    direccion = models.ForeignKey(
        Direccion,
        on_delete=models.CASCADE,
        related_name='sucursales',
        verbose_name=_('Dirección'),
        help_text=_('Dirección de la sucursal'),
    )

    class Meta:
        verbose_name = _('Sucursal')
        verbose_name_plural = _('Sucursales')


class Empleado(models.Model):
    nombre = models.CharField(
        _('Nombre'),
        max_length=50,
        help_text=_('Nombre del empleado'),
    )
    apellido = models.CharField(
        _('Apellido'),
        max_length=50,
        help_text=_('Apellido del empleado'),
    )
    nro_documento = models.PositiveBigIntegerField(
        _('Número de documento'),
        help_text=_('Número de documento del empleado'),
    )
    fecha_contratacion = models.DateField(
        _('Fecha de contratación'),
        help_text=_('Fecha en la que fue contratado'),
    )

    def antiguedad(self):
        if self.fecha_contratacion:
            hoy = date.today()
            diferencia = hoy.year - self.fecha_contratacion.year

            # Si aún no cumplió el aniversario este año, restamos 1
            if (hoy.month, hoy.day) < (self.fecha_contratacion.month, self.fecha_contratacion.day):
                diferencia -= 1

            return f"{diferencia} años"
        return "0 años"

    direccion = models.ForeignKey(
        Direccion,
        on_delete=models.CASCADE,
        related_name='empleados',
        verbose_name=_('Dirección'),
        help_text=_('Dirección del empleado'),
    )
    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.CASCADE,
        related_name='empleados',
        verbose_name=_('Sucursal'),
        help_text=_('Sucursal donde trabaja'),
    )
    tipo_documento = models.ForeignKey(
        TipoDocumento,
        on_delete=models.PROTECT,
        verbose_name=_('Tipo de documento'),
        help_text=_('Tipo de documento del empleado'),
    )

    def __str__(self):
        return f"{self.nombre} {self.apellido} (Sucursal: {self.sucursal.nombre})"

    class Meta:
        verbose_name = _('Empleado')
        verbose_name_plural = _('Empleados')
        ordering = ['apellido', 'nombre']


class TipoVehiculo(NombreAbstract):
    class Meta:
        verbose_name = _('Tipo de vehículo')
        verbose_name_plural = _('Tipos de vehículo')


class Cliente(models.Model):
    nombre = models.CharField(
        _('Nombre'),
        max_length=50,
        help_text=_('Nombre del cliente'),
    )
    apellido = models.CharField(
        _('Apellido'),
        max_length=50,
        help_text=_('Apellido del cliente'),
    )
    telefono = models.CharField(
        _('Teléfono'),
        max_length=20,
        help_text=_('Número de teléfono'),
        blank=True,
        null=True,
    )
    nro_documento = models.PositiveBigIntegerField(
        _('Número de documento'),
        help_text=_('Número de documento del cliente'),
    )
    tipo_documento = models.ForeignKey(
        TipoDocumento,
        on_delete=models.PROTECT,
        verbose_name=_('Tipo de documento'),
        help_text=_('Tipo de documento del cliente'),
    )
    direccion = models.ForeignKey(
        Direccion,
        on_delete=models.CASCADE,
        related_name='clientes',
        verbose_name=_('Dirección'),
        help_text=_('Dirección del cliente'),
    )

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        verbose_name = _('Cliente')
        verbose_name_plural = _('Clientes')
        ordering = ['apellido', 'nombre']
        indexes = [
            models.Index(fields=['nro_documento']),
        ]


class Vehiculo(models.Model):
    patente = models.CharField(
        _('Patente'),
        max_length=10,
        primary_key=True,
        help_text=_('Patente del vehículo'),
    )
    capacidad_carga = models.DecimalField(
        _('Capacidad de carga'),
        max_digits=10,
        decimal_places=2,
        help_text=_('Capacidad máxima de carga'),
    )
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='vehiculos',
        verbose_name=_('Empleado responsable'),
        help_text=_('Empleado asignado al vehículo'),
    )
    tipo_vehiculo = models.ForeignKey(
        TipoVehiculo,
        on_delete=models.PROTECT,
        verbose_name=_('Tipo de vehículo'),
        help_text=_('Tipo de vehículo'),
    )

    def capacidad_restante(self):
        carga_total = Paquete.objects.filter(
            envio__vehiculo=self
        ).aggregate(total=Sum('peso'))['total'] or 0
        return self.capacidad_carga - carga_total

    def __str__(self):
        return f"{self.patente} - {self.tipo_vehiculo.nombre}"

    class Meta:
        verbose_name = _('Vehículo')
        verbose_name_plural = _('Vehículos')
        ordering = ['patente']


class Envio(models.Model):
    fecha_envio = models.DateTimeField(
        _('Fecha de envío'),
        help_text=_('Fecha y hora del envío'),
    )
    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.CASCADE,
        related_name='envios',
        verbose_name=_('Sucursal'),
        help_text=_('Sucursal desde donde se envía'),
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='envios',
        verbose_name=_('Cliente'),
        help_text=_('Cliente que recibe el envío'),
    )
    estado = models.CharField(
        _('Estado'),
        max_length=50,
        help_text=_('Estado actual del envío'),
    )
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        related_name='envios',
        verbose_name=_('Vehículo'),
        help_text=_('Vehículo que realiza el envío'),
    )

    def __str__(self):
        return f"Envío #{self.pk} - {self.cliente} ({self.estado})"

    class Meta:
        verbose_name = _('Envío')
        verbose_name_plural = _('Envíos')
        ordering = ['-fecha_envio']


class Paquete(models.Model):
    peso = models.DecimalField(
        _('Peso'),
        max_digits=10,
        decimal_places=2,
        help_text=_('Peso del paquete en kg'),
    )
    ancho = models.DecimalField(
        _('Ancho en cm2'),
        max_digits=10,
        decimal_places=2,
        help_text=_('Ancho del paquete en cm'),
    )
    alto = models.DecimalField(
        _('Alto en cm2'),
        max_digits=10,
        decimal_places=2,
        help_text=_('Alto del paquete en cm'),
    )
    longitud = models.DecimalField(
        _('Longitud en cm2'),
        max_digits=10,
        decimal_places=2,
        help_text=_('Longitud del paquete en cm'),
    )

    def dimensiones (self):
        if self.ancho and self.alto and self.longitud:
            dimensiones = self.ancho * self.alto * self.longitud
            return f"{dimensiones:.2f} cm³"
        return "0.00 cm³"
    
    descripcion = models.CharField(
        _('Descripción'),
        max_length=250,
        help_text=_('Descripción del contenido del paquete'),
    )
    envio = models.ForeignKey(
        Envio,
        on_delete=models.CASCADE,
        related_name='paquetes',
        verbose_name=_('Envío'),
        help_text=_('Envío al que pertenece el paquete'),
    )

    def __str__(self):
        return f"Paquete #{self.pk} del Envío #{self.envio.pk}"

    class Meta:
        verbose_name = _('Paquete')
        verbose_name_plural = _('Paquetes')
```

---

## 10. Administración de la Aplicación

### Ejemplo de `admin.py`
Registra tus modelos para gestionarlos desde el panel de administración de Django.

> **Puedes copiar todo este bloque y pegarlo directamente en tu archivo ./src/pastas/admin.py.**
```python
from django.contrib import admin
from .models import (
    Provincia, Ciudad, Direccion, TipoDocumento, Sucursal,
    Empleado, TipoVehiculo, Cliente, Vehiculo, Envio, Paquete
)

@admin.register(Provincia)
class ProvinciaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre")
    search_fields = ("nombre",)

@admin.register(Ciudad)
class CiudadAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "provincia")
    list_filter = ("provincia",)
    search_fields = ("nombre",)

@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = ("id", "calle", "numero", "ciudad")
    list_filter = ("ciudad",)
    search_fields = ("calle",)

@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre")
    search_fields = ("nombre",)

@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "direccion")
    search_fields = ("nombre",)

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "apellido", "nro_documento", "fecha_contratacion", "sucursal", )
    list_filter = ("sucursal", "tipo_documento")
    search_fields = ("nombre", "apellido")

@admin.register(TipoVehiculo)
class TipoVehiculoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre")
    search_fields = ("nombre",)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "apellido", "telefono", "nro_documento")
    search_fields = ("nombre", "apellido", "nro_documento")

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ("patente", "tipo_vehiculo", "empleado", "capacidad_carga", "capacidad_restante")
    search_fields = ("patente",)


@admin.register(Envio)
class EnvioAdmin(admin.ModelAdmin):
    list_display = ("id", "fecha_envio", "cliente", "sucursal", "estado", "vehiculo")
    list_filter = ("estado", "sucursal", "fecha_envio")
    search_fields = ("cliente__nombre", "cliente__apellido")

@admin.register(Paquete)
class PaqueteAdmin(admin.ModelAdmin):
    list_display = ("id", "peso", "ancho", "alto","longitud", "envio", "dimensiones")
    list_filter = ("envio",)

```

---

## 11. Migraciones y Carga de Datos Iniciales

### Realizar migraciones de la app nueva.
> **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
```sh
docker compose run --rm manage makemigrations
docker compose run --rm manage migrate
```

Accede a la administración de Django en [http://localhost:8000/admin/](http://localhost:8000/admin/) donde ya se van a ver los cambios realizados en la app, pero todavía sin datos pre cargados.

### Crear y cargar fixtures (datos iniciales)
Crea la carpeta `./src/transporte/fixtures` dentro de tu app y agrega el archivo `initial_data.json` con los datos de ejemplo. Luego, carga los datos:
> **Puedes copiar todo este bloque y pegarlo directamente en tu archivo initial_data.json.**
```json
[
    {
        "model": "transporte.tipodocumento",
        "pk": 1,
        "fields": {
            "nombre": "DNI"
        }
    },
    {
        "model": "transporte.tipodocumento",
        "pk": 2,
        "fields": {
            "nombre": "CUIT"
        }
    },
    {
        "model": "transporte.provincia",
        "pk": 1,
        "fields": {
            "nombre": "Buenos Aires"
        }
    },
    {
        "model": "transporte.provincia",
        "pk": 2,
        "fields": {
            "nombre": "Córdoba"
        }
    },
    {
        "model": "transporte.ciudad",
        "pk": 1,
        "fields": {
            "nombre": "La Plata",
            "provincia": 1
        }
    },
    {
        "model": "transporte.ciudad",
        "pk": 2,
        "fields": {
            "nombre": "Córdoba Capital",
            "provincia": 2
        }
    },
    {
        "model": "transporte.direccion",
        "pk": 1,
        "fields": {
            "calle": "Av. 7",
            "numero": 1234,
            "ciudad": 1
        }
    },
    {
        "model": "transporte.direccion",
        "pk": 2,
        "fields": {
            "calle": "Av. Colón",
            "numero": 456,
            "ciudad": 2
        }
    },
    {
        "model": "transporte.sucursal",
        "pk": 1,
        "fields": {
            "nombre": "Sucursal Central",
            "direccion": 1
        }
    },
    {
        "model": "transporte.sucursal",
        "pk": 2,
        "fields": {
            "nombre": "Sucursal Norte",
            "direccion": 2
        }
    },
    {
        "model": "transporte.tipovehiculo",
        "pk": 1,
        "fields": {
            "nombre": "Camión"
        }
    },
    {
        "model": "transporte.tipovehiculo",
        "pk": 2,
        "fields": {
            "nombre": "Camioneta"
        }
    },
    {
        "model": "transporte.empleado",
        "pk": 1,
        "fields": {
            "nombre": "Juan",
            "apellido": "Pérez",
            "nro_documento": 30123456,
            "fecha_contratacion": "2018-05-20",
            "direccion": 1,
            "sucursal": 1,
            "tipo_documento": 1
        }
    },
    {
        "model": "transporte.cliente",
        "pk": 1,
        "fields": {
            "nombre": "Laura",
            "apellido": "Gómez",
            "telefono": "3512345678",
            "nro_documento": 32000444,
            "tipo_documento": 1,
            "direccion": 1
        }
    },
    {
        "model": "transporte.vehiculo",
        "pk": "AA123BB",
        "fields": {
            "capacidad_carga": "1000.00",
            "empleado": 1,
            "tipo_vehiculo": 1
        }
    },
    {
        "model": "transporte.envio",
        "pk": 1,
        "fields": {
            "fecha_envio": "2024-06-18T10:00:00Z",
            "sucursal": 1,
            "cliente": 1,
            "estado": "En camino",
            "vehiculo": "AA123BB"
        }
    },
    {
        "model": "transporte.paquete",
        "pk": 1,
        "fields": {
            "peso": "5.50",
            "ancho": "20.00",
            "alto": "15.00",
            "longitud": "30.00",
            "descripcion": "Libros escolares",
            "envio": 1
        }
    }
]

```
> **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
```sh
docker compose run --rm manage loaddata initial_data
```

---

## Conclusión
Con estos pasos, tendrás un entorno Django profesional, portable y listo para desarrollo o producción. Recuerda consultar la documentación oficial de Django y Docker para profundizar en cada tema. ¡Éxitos en tu proyecto!

---