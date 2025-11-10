import json
import logging
from typing import Dict

import requests
from django.conf import settings
from django.core.mail import EmailMessage
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from inlinestyler.utils import inline_css

from lacrei_models.notification.exceptions import SMSError
from lacrei_models.notification.models import Notification
from lacrei_models.notification.template_context_models import get_base_email_context
from lacrei_models.notification.utils import mask_email

logger = logging.getLogger(__name__)


class NotificationService:
    @classmethod
    def send(cls, template_prefix, email, context, recipient):
        send_to = [email] if isinstance(email, str) else email
        context_to_save = context.copy()
        with_base_email_context = context_to_save.pop("has_base_email_context", False)

        masked_recipients = [mask_email(recipient) for recipient in send_to]

        notification = Notification.objects.create(
            template_prefix=template_prefix,
            json_context=context_to_save,
            send_to=send_to,
            recipient=recipient,
            subject=EmailBackendService.render_mail_subject(template_prefix, context),
        )

        context_to_render = context_to_save.copy()
        if with_base_email_context:
            context_to_render |= get_base_email_context()

        email_message = EmailBackendService.build_email_message(
            template_prefix, context_to_render, send_to, notification.subject
        )

        try:
            email_message.send()
        except Exception as exc:  # pragma: no cover
            notification.error_message = f"{type(exc).__name__}: {exc}"
            notification.status = "error"
            logger.error(
                f"Erro no envio de email - Template: {template_prefix}, "
                f"Para: {masked_recipients}, Erro: {exc}"
            )
        else:
            notification.status = "success"
            logger.info(
                f"Email enviado com sucesso - Template: {template_prefix}, "
                f"Para: {masked_recipients}"
            )

        notification.save()


class EmailBackendService:
    @classmethod
    def render_mail_html(cls, template_prefix, context) -> dict:
        bodies = {}
        for ext in ["html"]:
            try:
                template_name = "{0}_message.{1}".format(template_prefix, ext)
                bodies[ext] = render_to_string(
                    template_name,
                    context,
                    None,
                ).strip()
                bodies[ext] = inline_css(bodies[ext])

            except TemplateDoesNotExist:  # pragma: no cover
                if ext == "txt" and not bodies:
                    # We need at least one body
                    raise
        return bodies

    @classmethod
    def render_mail_subject(cls, template_prefix: str, context: Dict[str, str]) -> str:
        subject_template = render_to_string(
            "{0}_subject.txt".format(template_prefix), context
        )
        subject = " ".join(subject_template.splitlines()).strip()
        return f"{settings.ACCOUNT_EMAIL_SUBJECT_PREFIX}{subject}"

    @classmethod
    def build_email_message(cls, template_prefix, context, send_to, subject):
        bodies = cls.render_mail_html(template_prefix, context)
        msg = EmailMessage(
            subject, bodies["html"], settings.DEFAULT_FROM_EMAIL, send_to
        )
        msg.content_subtype = "html"  # Main content is now text/html
        return msg


class SMSService:
    @classmethod
    def send(cls, phone_number, message):
        payload = [
            {
                "key": settings.SMS_DEV_TOKEN,
                "type": 9,
                "number": phone_number,
                "msg": message,
            }
        ]

        try:
            response = requests.post(
                settings.SMS_DEV_URL, json.dumps(payload), timeout=4
            )
            response.raise_for_status()
            data = response.json()
            if not data[0]["situacao"] == "OK":
                raise requests.exceptions.RequestException
        except (
            ValueError,
            requests.exceptions.RequestException,
            requests.exceptions.Timeout,
        ) as e:
            raise SMSError() from e
