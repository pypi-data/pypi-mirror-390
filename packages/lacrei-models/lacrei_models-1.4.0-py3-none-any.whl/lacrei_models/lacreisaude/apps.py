from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LacreisaudeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "lacreisaude"
    label = "lacreisaude"
    verbose_name = _("Lacrei Saúde")
