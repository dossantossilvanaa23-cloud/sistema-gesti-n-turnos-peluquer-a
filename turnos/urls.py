from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from django.urls import reverse_lazy

from . import views
from .forms import StaffAuthenticationForm

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('mis-turnos/', views.mis_turnos, name='mis_turnos'),
    path(
        'panel/ingresar/',
        LoginView.as_view(
            template_name='turnos/panel_login.html',
            authentication_form=StaffAuthenticationForm,
            next_page=reverse_lazy('panel_admin'),
        ),
        name='panel_login',
    ),
    path(
        'panel/salir/',
        LogoutView.as_view(next_page=reverse_lazy('panel_login')),
        name='panel_logout',
    ),
    path('panel/', views.panel_admin, name='panel_admin'),
    path('comprobante/<int:turno_id>/', views.comprobante, name='comprobante'),
]