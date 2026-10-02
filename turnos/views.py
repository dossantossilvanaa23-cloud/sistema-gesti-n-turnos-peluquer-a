from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from .models import ESTADOS_TURNO, PRECIOS_SERVICIOS, Turno


def inicio(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        telefono = request.POST.get("telefono")
        servicio = request.POST.get("servicio")
        fecha = request.POST.get("fecha")
        hora = request.POST.get("hora")
        precio_servicio = PRECIOS_SERVICIOS.get(servicio)

        if precio_servicio is None:
            return HttpResponseBadRequest("El servicio seleccionado no es válido.")

        turno = Turno.objects.create(
            nombre_cliente=nombre,
            telefono=telefono,
            servicio=servicio,
            precio_servicio=precio_servicio,
            fecha=fecha,
            hora=hora,
            estado="Pendiente"
        )

        return redirect("comprobante", turno_id=turno.id)

    return render(request, "turnos/inicio.html")


def comprobante(request, turno_id):
    turno = Turno.objects.get(pk=turno_id)
    return render(request, "turnos/comprobante.html", {"turno": turno})


def mis_turnos(request):
    telefono = request.POST.get("telefono", "").strip()
    turnos = Turno.objects.none()

    if request.method == "POST" and telefono:
        turnos = Turno.objects.filter(telefono=telefono).order_by("fecha", "hora")

    return render(request, "turnos/mis_turnos.html", {
        "telefono": telefono,
        "turnos": turnos,
        "busqueda_realizada": request.method == "POST",
    })


@user_passes_test(lambda usuario: usuario.is_staff, login_url="panel_login")
def panel_admin(request):
    if request.method == "POST":
        turno = get_object_or_404(Turno, pk=request.POST.get("turno_id"))
        nuevo_estado = request.POST.get("estado")
        estados_validos = {valor for valor, _ in ESTADOS_TURNO}

        if nuevo_estado in estados_validos:
            turno.estado = nuevo_estado
            turno.save(update_fields=["estado"])
            messages.success(request, f"Turno #{turno.id}: estado actualizado.")
        else:
            messages.error(request, "El estado seleccionado no es válido.")

        return redirect("panel_admin")

    hoy = timezone.localdate()
    busqueda = request.GET.get("q", "").strip()
    estado_filtro = request.GET.get("estado", "")
    vista = request.GET.get("vista", "proximos")
    turnos = Turno.objects.all()

    if vista != "todos":
        turnos = turnos.filter(fecha__gte=hoy).exclude(estado="Cancelado")
    if busqueda:
        turnos = turnos.filter(
            Q(nombre_cliente__icontains=busqueda)
            | Q(telefono__icontains=busqueda)
            | Q(servicio__icontains=busqueda)
        )
    if estado_filtro:
        turnos = turnos.filter(estado=estado_filtro)

    pagina = Paginator(turnos.order_by("fecha", "hora"), 20).get_page(
        request.GET.get("pagina"),
    )

    return render(request, "turnos/panel_admin.html", {
        "pagina": pagina,
        "busqueda": busqueda,
        "estado_filtro": estado_filtro,
        "vista": vista,
        "estados": ESTADOS_TURNO,
        "total_turnos": Turno.objects.count(),
        "pendientes": Turno.objects.filter(estado="Pendiente").count(),
        "turnos_hoy": Turno.objects.filter(fecha=hoy).exclude(estado="Cancelado").count(),
        "proximos": Turno.objects.filter(fecha__gte=hoy).exclude(estado="Cancelado").count(),
        "hoy": hoy,
    })