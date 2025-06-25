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
