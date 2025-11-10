from django.urls import reverse
from pydantic import HttpUrl

from lacrei_models.utils.template_context_models import WithBaseEmailContext


class EmailConfirmationContext(WithBaseEmailContext):
    activate_url: HttpUrl
    receiver_name: str = "Usuário"

    @classmethod
    def _convert_from_pickled_content_to_this_model_args(
        cls, pickled_context: dict
    ) -> dict:
        activate_url = pickled_context.get("activate_url", "")
        receiver_name = pickled_context.get("receiver_name", "Usuário")
        return {"activate_url": activate_url, "receiver_name": receiver_name}


class EmailConfirmationSignupContext(EmailConfirmationContext):
    _template_prefix: str = "account/email/email_confirmation_signup"


class PasswordResetContext(WithBaseEmailContext):
    _template_prefix: str = "registration/password_reset"
    password_reset_confirm_url: HttpUrl
    uid: str
    token: str

    @classmethod
    def _convert_from_pickled_content_to_this_model_args(
        self, pickled_context: dict
    ) -> dict:
        domain = pickled_context["domain"]
        protocol = pickled_context["protocol"]
        uid = pickled_context["uid"]
        token = pickled_context["token"]

        user = pickled_context.get("user")
        is_professional = user and hasattr(user, "professional")

        if is_professional:
            from django.conf import settings

            professional_domain = settings.PROFESSIONAL_LOGIN_URL.rstrip("/")
            if not professional_domain.startswith(("http://", "https://")):
                professional_domain = f"https://{professional_domain}"
            password_reset_confirm_url = (
                f"{professional_domain}/saude/profissional/redefinir-senha/confirmar/"
            )
        else:
            password_reset_confirm_url = (
                f"{protocol}://{domain}{reverse('password_reset_confirm')}"
            )

        return {
            "password_reset_confirm_url": password_reset_confirm_url,
            "uid": uid,
            "token": token,
        }


class AccountDeactivatedContext(WithBaseEmailContext):
    _template_prefix: str = "account/email/account_deactivated"
    receiver_name: str
    reactivate_url: HttpUrl

    @classmethod
    def _convert_from_pickled_content_to_this_model_args(
        cls, pickled_context: dict
    ) -> dict:
        receiver_name = pickled_context.get("receiver_name", "Usuário")
        reactivate_url = pickled_context.get("reactivate_url", "")
        return {
            "receiver_name": receiver_name,
            "reactivate_url": reactivate_url,
        }


class AccountDeletedContext(WithBaseEmailContext):
    _template_prefix: str = "account/email/account_deleted"
    receiver_name: str
    signup_url: HttpUrl

    @classmethod
    def _convert_from_pickled_content_to_this_model_args(
        cls, pickled_context: dict
    ) -> dict:
        receiver_name = pickled_context.get("receiver_name", "Usuário")
        signup_url = pickled_context.get("signup_url", "")
        return {
            "receiver_name": receiver_name,
            "signup_url": signup_url,
        }
