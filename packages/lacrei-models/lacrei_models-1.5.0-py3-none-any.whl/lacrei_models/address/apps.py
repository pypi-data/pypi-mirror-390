from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AddressConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "address"
    label = "address"
    verbose_name = _("Endereços")
