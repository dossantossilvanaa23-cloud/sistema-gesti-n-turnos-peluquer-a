from django.contrib import admin
from .models import Turno


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nombre_cliente",
        "telefono",
        "servicio",
        "mostrar_costo",
        "fecha",
        "hora",
        "estado",
    )
    list_display_links = ("id", "nombre_cliente")
    list_editable = ("estado",)
    list_filter = ("estado", "servicio", "fecha")
    search_fields = ("nombre_cliente", "telefono", "servicio")
    date_hierarchy = "fecha"
    ordering = ("fecha", "hora")
    list_per_page = 25

    @admin.display(description="Costo")
    def mostrar_costo(self, turno):
        return f"$ {turno.precio_servicio_formateado}"
