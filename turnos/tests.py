from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Turno


class ReservaTurnoTests(TestCase):
    def test_reservar_redirige_al_comprobante(self):
        respuesta = self.client.post("/", {
            "nombre": "Ana Pérez",
            "telefono": "3755691919",
            "servicio": "Corte",
            "fecha": "2026-10-01",
            "hora": "09:00",
        })

        turno = Turno.objects.get()

        self.assertRedirects(respuesta, f"/comprobante/{turno.id}/")
        self.assertEqual(turno.fecha, date(2026, 10, 1))
        self.assertEqual(turno.hora, time(9, 0))
        self.assertEqual(turno.precio_servicio, 8000)

    def test_comprobante_muestra_los_datos_del_turno(self):
        turno = Turno.objects.create(
            nombre_cliente="Ana Pérez",
            telefono="3755691919",
            servicio="Corte",
            precio_servicio=8000,
            fecha=date(2026, 10, 1),
            hora=time(9, 0),
        )

        respuesta = self.client.get(f"/comprobante/{turno.id}/")

        self.assertContains(respuesta, "Turno reservado")
        self.assertContains(respuesta, "Ana Pérez")
        self.assertContains(respuesta, "01/10/2026")
        self.assertContains(respuesta, "$ 8.000")

    def test_mis_turnos_solo_muestra_los_del_telefono_consultado(self):
        Turno.objects.create(
            nombre_cliente="Ana Pérez",
            telefono="3755691919",
            servicio="Corte",
            precio_servicio=8000,
            fecha=date(2026, 10, 1),
            hora=time(9, 0),
        )
        Turno.objects.create(
            nombre_cliente="Otra persona",
            telefono="1111111111",
            servicio="Color",
            precio_servicio=15000,
            fecha=date(2026, 10, 2),
            hora=time(10, 0),
        )

        respuesta = self.client.post("/mis-turnos/", {"telefono": "3755691919"})

        self.assertContains(respuesta, "Ana Pérez")
        self.assertNotContains(respuesta, "Otra persona")


class TurnoAdminTests(TestCase):
    def test_panel_admin_lista_turnos_y_permite_busqueda(self):
        usuario_admin = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="clave-segura-de-prueba",
        )
        self.client.force_login(usuario_admin)
        Turno.objects.create(
            nombre_cliente="Ana Pérez",
            telefono="3755691919",
            servicio="Corte",
            precio_servicio=8000,
            fecha=date(2026, 10, 1),
            hora=time(9, 0),
        )

        respuesta = self.client.get(
            reverse("admin:turnos_turno_changelist"),
            {"q": "3755691919"},
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Ana Pérez")
        self.assertContains(respuesta, "$ 8.000")


class PanelAdministrativoTests(TestCase):
    def setUp(self):
        self.usuario_staff = get_user_model().objects.create_user(
            username="mariela",
            password="clave-segura-de-prueba",
            is_staff=True,
        )
        self.turno = Turno.objects.create(
            nombre_cliente="Ana Pérez",
            telefono="3755691919",
            servicio="Corte",
            precio_servicio=8000,
            fecha=timezone.localdate() + timedelta(days=1),
            hora=time(9, 0),
        )

    def test_panel_solicita_ingreso_a_usuarios_no_autenticados(self):
        respuesta = self.client.get(reverse("panel_admin"))

        self.assertRedirects(
            respuesta,
            f"{reverse('panel_login')}?next={reverse('panel_admin')}",
        )

    def test_usuario_staff_ingresa_al_panel_personalizado(self):
        respuesta = self.client.post(reverse("panel_login"), {
            "username": "mariela",
            "password": "clave-segura-de-prueba",
            "next": reverse("panel_admin"),
        }, follow=True)

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Agenda de turnos")
        self.assertContains(respuesta, "Ana Pérez")
        self.assertContains(respuesta, "$ 8.000")

    def test_usuario_sin_permisos_no_puede_ingresar(self):
        get_user_model().objects.create_user(
            username="cliente",
            password="clave-segura-de-prueba",
        )

        respuesta = self.client.post(reverse("panel_login"), {
            "username": "cliente",
            "password": "clave-segura-de-prueba",
        })

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "no tiene permisos")

    def test_staff_puede_actualizar_estado_desde_el_panel(self):
        self.client.force_login(self.usuario_staff)

        respuesta = self.client.post(reverse("panel_admin"), {
            "turno_id": self.turno.id,
            "estado": "Confirmado",
        })

        self.turno.refresh_from_db()
        self.assertRedirects(respuesta, reverse("panel_admin"))
        self.assertEqual(self.turno.estado, "Confirmado")
