from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AddressConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "lacrei_models.address"
    label = "address"
    verbose_name = _("Endereços")
