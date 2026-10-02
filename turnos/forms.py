from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError


class StaffAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "class": "campo",
            "autocomplete": "username",
            "placeholder": "Usuario",
        })
        self.fields["password"].widget.attrs.update({
            "class": "campo",
            "autocomplete": "current-password",
            "placeholder": "Contraseña",
        })

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise ValidationError(
                "Esta cuenta no tiene permisos para ingresar al panel.",
                code="no_staff_access",
            )