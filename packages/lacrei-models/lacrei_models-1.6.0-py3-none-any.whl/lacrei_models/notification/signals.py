import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_delete, post_save, pre_delete, pre_save
from django.dispatch import Signal, receiver

from lacrei_models.lacreiid.models import User
from lacrei_models.notification.services import NotificationService

logger = logging.getLogger(__name__)

_user_delete_context = {}

notification = Signal()


@receiver(notification)
def send_notification(sender, template_prefix, email, context, recipient, **kwargs):
    """
    Escuta o sinal de notificação, tenta enviar o e-mail e, em caso de falha,
    loga o erro de forma apropriada e o relança para o Celery.
    """
    try:
        NotificationService.send(template_prefix, email, context, recipient)
    except Exception as e:
        logger.critical(
            f"FALHA CRÍTICA AO ENVIAR NOTIFICAÇÃO! Template: {template_prefix}, Erro: {e}",
            exc_info=True,
        )

        raise


@receiver(pre_delete, sender=User)
def store_user_context_before_delete(sender, instance, **kwargs):
    """
    Guarda o contexto de um usuário momentos ANTES de ele ser deletado,
    para ser usado no sinal post_delete.
    """
    context = {
        "is_professional": False,
        "name": instance.get_full_name(),
        "email": instance.email,
    }
    try:
        professional_profile = instance.professional
        context["is_professional"] = True
        context["name"] = professional_profile.full_name
    except (ObjectDoesNotExist, AttributeError):
        pass
    _user_delete_context[instance.pk] = context


@receiver(post_delete, sender=User)
def send_account_deleted_notification(sender, instance, **kwargs):
    """
    Envia notificação após um usuário ser deletado de verdade do banco,
    usando o contexto salvo pelo `pre_delete` para saber se era profissional.
    """
    user_context = _user_delete_context.pop(instance.pk, None)
    if not user_context:
        return

    template_prefix = (
        "account/email/professional_account_deleted"
        if user_context["is_professional"]
        else "account/email/patient_account_deleted"
    )
    NotificationService.send(
        template_prefix=template_prefix,
        email=user_context["email"],
        context={"user_name": user_context["name"]},
        recipient=instance,
    )


@receiver(post_save, sender=User)
def send_account_suspended_notification(sender, instance, created, **kwargs):
    """
    Envia notificação quando um usuário é suspenso (is_active=False).
    Verifica se o usuário é um profissional para enviar o e-mail correto.
    """
    if created or instance.is_active:
        return

    if hasattr(instance, "professional"):
        NotificationService.send(
            template_prefix="account/email/professional_account_suspended",
            email=instance.email,
            context={"professional_name": instance.professional.full_name},
            recipient=instance,
        )
    else:
        NotificationService.send(
            template_prefix="account/email/patient_account_suspended",
            email=instance.email,
            context={
                "user_name": instance.get_full_name(),
                "reason": "Violação dos termos de serviço",
            },
            recipient=instance,
        )


@receiver(pre_save, sender="lacreisaude.Professional")
def store_previous_professional_state(sender, instance, **kwargs):
    """
    Antes de salvar um profissional, armazena o estado anterior do campo `active`.
    Garante que suspensões diretas no modelo Professional também sejam capturadas.
    """
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._was_active_before = old_instance.active
        except ObjectDoesNotExist:
            instance._was_active_before = False


@receiver(post_save, sender="lacreisaude.Professional")
def send_professional_suspended_notification(sender, instance, created, **kwargs):
    """
    Envia um e-mail APENAS se o profissional mudou de ativo para inativo.
    Garante que suspensões diretas no modelo Professional também sejam capturadas.
    """
    if created:
        return

    was_active_before = getattr(instance, "_was_active_before", False)
    is_inactive_now = not instance.active

    if was_active_before and is_inactive_now:
        NotificationService.send(
            template_prefix="account/email/professional_account_suspended",
            email=instance.user.email,
            context={"professional_name": instance.full_name},
            recipient=instance.user,
        )
