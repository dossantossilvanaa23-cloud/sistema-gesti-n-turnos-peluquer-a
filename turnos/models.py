from django.db import models

# Create your models here.
PRECIOS_SERVICIOS = {
    "Corte": 8000,
    "Color": 15000,
    "Peinado": 10000,
    "Tratamiento": 12000,
}
ESTADOS_TURNO = (
    ("Pendiente", "Pendiente"),
    ("Confirmado", "Confirmado"),
    ("Completado", "Completado"),
    ("Cancelado", "Cancelado"),
)


class Turno(models.Model):
    nombre_cliente = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    servicio = models.CharField(max_length=100)
    precio_servicio = models.PositiveIntegerField(default=0)
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_TURNO,
        default="Pendiente",
    )

    @property
    def precio_servicio_formateado(self):
        return f"{self.precio_servicio:,}".replace(",", ".")

    def __str__(self):
        return f"{self.nombre_cliente} - {self.servicio} - {self.fecha}"
