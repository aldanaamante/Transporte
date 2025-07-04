from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from datetime import date
from django.core.exceptions import ValidationError


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
    def clean(self):
        super().clean()
        if Provincia.objects.exclude(pk=self.pk).filter(nombre=self.nombre).exists():
            raise ValidationError({'nombre': 'Ya existe una provincia con este nombre.'})

    class Meta(NombreAbstract.Meta):
        verbose_name = _('Provincia')
        verbose_name_plural = _('Provincias')
        constraints = [
            models.UniqueConstraint(fields=['nombre'], name='unique_provincia_nombre')
        ]


class Ciudad(NombreAbstract):
    provincia = models.ForeignKey(
        Provincia,
        on_delete=models.CASCADE,
        related_name='ciudades',
        verbose_name=_('Provincia'),
        help_text=_('Provincia a la que pertenece la ciudad'),
    )

    def clean(self):
        super().clean()
        if Ciudad.objects.exclude(pk=self.pk).filter(nombre=self.nombre, provincia=self.provincia).exists():
            raise ValidationError({'nombre': _('Ya existe una ciudad con este nombre en esta provincia.')})

    class Meta(NombreAbstract.Meta):
        verbose_name = _('Ciudad')
        verbose_name_plural = _('Ciudades')
        constraints = [
            models.UniqueConstraint(fields=['nombre', 'provincia'], name='unique_ciudad_nombre_provincia')
        ]


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

    def clean(self):
        calle_mayus = self.calle.upper() if self.calle else ''
        existe = Direccion.objects.exclude(pk=self.pk).filter(
            ciudad=self.ciudad,
            calle=calle_mayus,
            numero=self.numero
        ).exists()
        if existe:
            raise ValidationError({'numero': _('Ya existe una dirección con esa calle y número en esta ciudad.')})

    def save(self, *args, **kwargs):
        if self.calle:
            self.calle = self.calle.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.calle} {self.numero}, {self.ciudad.nombre}"

    class Meta:
        verbose_name = _('Dirección')
        verbose_name_plural = _('Direcciones')
        ordering = ['ciudad__nombre', 'calle']
        constraints = [
            models.UniqueConstraint(
                fields=['calle', 'numero', 'ciudad'],
                name='unique_direccion'
            )
        ]


class TipoDocumento(NombreAbstract):
    def clean(self):
        super().clean()
        if TipoDocumento.objects.exclude(pk=self.pk).filter(nombre=self.nombre).exists():
            raise ValidationError({'nombre': _('Ya existe un tipo de documento con este nombre.')})

    class Meta(NombreAbstract.Meta):
        verbose_name = _('Tipo de documento')
        verbose_name_plural = _('Tipos de documento')
        constraints = [
            models.UniqueConstraint(fields=['nombre'], name='unique_tipo_documento_nombre')
        ]



class Sucursal(NombreAbstract):
    direccion = models.ForeignKey(
        Direccion,
        on_delete=models.CASCADE,
        related_name='sucursales',
        verbose_name=_('Dirección'),
        help_text=_('Dirección de la sucursal'),
    )

    def clean(self):
        super().clean()
        if Sucursal.objects.exclude(pk=self.pk).filter(nombre=self.nombre).exists():
            raise ValidationError({'nombre': _('Ya existe una sucursal con este nombre.')})

    class Meta(NombreAbstract.Meta):
        verbose_name = _('Sucursal')
        verbose_name_plural = _('Sucursales')
        constraints = [
            models.UniqueConstraint(fields=['nombre'], name='unique_sucursal_nombre')
        ]


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
        unique=True,
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
    def clean(self):
        super().clean()
        if TipoVehiculo.objects.exclude(pk=self.pk).filter(nombre=self.nombre).exists():
            raise ValidationError({'nombre': _('Ya existe un tipo de vehículo con este nombre.')})

    class Meta(NombreAbstract.Meta):
        verbose_name = _('Tipo de vehículo')
        verbose_name_plural = _('Tipos de vehículo')
        constraints = [
            models.UniqueConstraint(fields=['nombre'], name='unique_tipo_vehiculo_nombre')
        ]


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
        unique=True,
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
            envio__vehiculo=self,
            envio__estado=Envio.EstadoEnvio.EN_CAMINO  # Uso del valor del choice
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

    class EstadoEnvio(models.TextChoices):
        EN_CAMINO = 'EN_CAMINO', _('En camino')
        ENTREGADO = 'ENTREGADO', _('Entregado')

    estado = models.CharField(
        _('Estado'),
        max_length=20,
        choices=EstadoEnvio.choices,
        default=EstadoEnvio.EN_CAMINO,
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
