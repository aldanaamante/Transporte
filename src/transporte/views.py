from django.shortcuts import render


from django.db.models import Count, Sum, Max, Avg
from django.utils import timezone
from datetime import timedelta

# 1. Total de paquetes y peso total por envío, ordenados por peso descendente
envios = Envio.objects.annotate(
    total_paquetes=Count('paquetes'),
    peso_total=Sum('paquetes__peso')
).order_by('-peso_total')

# 2. Empleados con la cantidad de vehículos que manejan
empleados = Empleado.objects.annotate(
    cantidad_vehiculos=Count('vehiculos')
).order_by('-cantidad_vehiculos')

# 3. Sucursales con al menos 5 empleados
sucursales = Sucursal.objects.annotate(
    cantidad_empleados=Count('empleados')
).filter(cantidad_empleados__gte=5)

# 4. Vehículos que transportaron paquetes > 50 kg en el último mes
hace_un_mes = timezone.now() - timedelta(days=30)
vehiculos = Vehiculo.objects.filter(
    envios__fecha_envio__gte=hace_un_mes,
    envios__paquetes__peso__gt=50
).distinct()

# 5. Clientes con la fecha del último envío que hicieron
clientes = Cliente.objects.annotate(
    ultima_fecha_envio=Max('envios__fecha_envio')
).order_by('-ultima_fecha_envio')

# 6. Provincia con más ciudades
provincia = Provincia.objects.annotate(
    cantidad_ciudades=Count('ciudades')
).order_by('-cantidad_ciudades').first()

# 7. Empleados que trabajan en sucursales ubicadas en una provincia específica
empleados_provincia = Empleado.objects.filter(
    sucursal__direccion__ciudad__provincia__nombreProvincia="Santa Fe"
)

# 8. Paquetes con descripción que contiene la palabra "fragil" (case-insensitive)
paquetes_fragil = Paquete.objects.filter(descripcion__icontains="fragil")

# 9. Cantidad de envíos y peso promedio por tipo de vehículo
resultados_tipo_vehiculo = TipoVehiculo.objects.annotate(
    cantidad_envios=Count('vehiculos__envios'),
    peso_promedio=Avg('vehiculos__envios__paquetes__peso')
)

# 10. Empleados sin vehículos asignados
empleados_sin_vehiculos = Empleado.objects.annotate(
    cantidad_vehiculos=Count('vehiculos')
).filter(cantidad_vehiculos=0)

