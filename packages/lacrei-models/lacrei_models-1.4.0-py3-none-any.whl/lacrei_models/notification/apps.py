from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NotificationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "lacrei_models.notification"
    label = "notification"
    verbose_name = _("Notificação")
