import logging

from django.core import serializers
from django.utils.functional import cached_property

from lacrei_models.lacreiid.adapters import AccountAdapter
from lacrei_models.notification.signals import notification
from lacrei_models.utils.sites import format_professional_url

from ..template_context_models import (
    BoardVerificationNumberRejectedContext,
    PostRegistrationApprovedContext,
    PostRegistrationRejectedContext,
)
from .constants import (
    BOARD_VERIFICATION_NOT_APPROVED_YET,
    PROFESSIONAL_ALREADY_APPROVED_FOR_STEP,
    PROFESSIONAL_VALIDATION_PENDING_ADMIN,
    PROFESSIONAL_VALIDATION_PENDING_DATA_INPUT,
)
from .exceptions import CannotSetStatusError

logger = logging.getLogger(__name__)


class VerificationStep:
    name: str
    url_path_to_submit: str
    url_path_to_wait_completion: str
    description: str

    def __init__(self, professional):
        self.professional = professional

    @cached_property
    def is_completed(self):  # pragma: no cover
        raise NotImplementedError

    @cached_property
    def is_submitted(self):  # pragma: no cover
        raise NotImplementedError

    @cached_property
    def redirect_to(self):
        if self.is_completed:
            return None

        if self.is_submitted:
            return self.url_path_to_wait_completion

        return self.url_path_to_submit

    def to_representation(self):
        return {
            "is_completed": self.is_completed,
            "is_submitted": self.is_submitted,
            "redirect_to": self.redirect_to,
            "description": self.description,
            "internal_message": (
                PROFESSIONAL_ALREADY_APPROVED_FOR_STEP
                if self.is_completed
                else (
                    PROFESSIONAL_VALIDATION_PENDING_DATA_INPUT
                    if not self.is_submitted
                    else PROFESSIONAL_VALIDATION_PENDING_ADMIN
                )
            ),
        }

    def set_approved(self, professsional_review, request=None):  # pragma: no cover
        raise NotImplementedError

    def set_rejected(self, professsional_review, request=None):  # pragma: no cover
        raise NotImplementedError


class BoardRegistrationNumber(VerificationStep):
    """
    Uma pessoa interna da lacrei irá validar o número do conselho no respectivo portal."

    Após validação, será enviado um email de confirmação, onde:
    - Se rejeitado: apagamos o cadastro e pedimos para refazer, com um número certo.
    - Se aprovado: segue para o pós cadastro.
    """

    name = "board_registration_number"
    url_path_to_submit = "/"
    url_path_to_wait_completion = "/saude/verificacao-inscricao/"
    description = "1ª - Validação no conselho"

    @cached_property
    def is_completed(self):
        return self.professional.profile_status == "approved"

    @cached_property
    def is_submitted(self):
        return True

    def set_approved(self, professsional_review, request=None):
        if self.professional.profile_status == "approved":
            raise CannotSetStatusError(PROFESSIONAL_ALREADY_APPROVED_FOR_STEP)

        self.professional.profile_status = "approved"
        self.professional.save(update_fields=["profile_status"])

        # Log da aprovação da etapa
        logger.info(
            "Etapa de validação aprovada: %s - Profissional ID: %s",
            self.description,
            self.professional.id,
        )

        AccountAdapter().send_confirmation_professional(self.professional.user, request)

    def set_rejected(self, professional_review, request=None):
        if self.professional.profile_status == "approved":
            raise CannotSetStatusError(PROFESSIONAL_ALREADY_APPROVED_FOR_STEP)

        user = self.professional.user
        email = user.email

        professional_review.rejected_professional_data = {
            "name": professional_review.professional_name,
            "profession": self.professional.profession.name,
            "state": self.professional.state.code,
            "board_registration_number": self.professional.board_registration_number,
            "email": email,
        }
        email_context = BoardVerificationNumberRejectedContext().model_dump(mode="json")
        user.profile.delete()
        self.professional.delete()
        user.delete()
        professional_review.professional = None
        professional_review.save()

        notification.send(
            sender=self,
            template_prefix="verification/board_verification_number_rejected",
            email=email,
            context=email_context,
            recipient=None,
        )


class EmailConfirmation(VerificationStep):
    """
    Nessa etapa, uma pessoa interna da Lacrei já aprovou o cadastro,
    e agora aguardamos a pessoa profissional confirmar o email.
    """

    name = "email_confirmation"
    url_path_to_submit = "/"
    url_path_to_wait_completion = "/saude/verificacao-inscricao/"
    description = "2ª - Confirmação do email"

    @cached_property
    def is_completed(self):
        return self.professional.user.email_verified

    @cached_property
    def is_submitted(self):
        # Se a etapa anterior (BoardRegistrationNumber) foi aprovada,
        # então esta etapa está automaticamente "submitted"
        return BoardRegistrationNumber(self.professional).is_completed


class PostRegistrationData(VerificationStep):
    """
    Nessa passo a pessoa profissional irá enviar os dados restantes para o cadastro.

    Após validação, será enviado um email de confirmação, onde:
    - Se rejeitado: mandamos email pedindo para reenviar os dados.
    - Se aprovado: Liberado para ficar ativo na plataforma
    """

    name = "post_registration_data"
    url_path_to_submit = "/saude/cadastro-dados-pessoais/"
    url_path_to_wait_completion = "/saude/painel-cadastro-analise/"
    description = "4ª - Pós cadastro"

    @cached_property
    def is_completed(self):
        return self.professional.active

    @cached_property
    def is_submitted(self):
        return hasattr(self.professional, "clinic") and bool(
            self.professional.board_certification_selfie
        )

    def set_approved(self, professsional_review, request=None):
        if self.is_completed:
            raise CannotSetStatusError(PROFESSIONAL_ALREADY_APPROVED_FOR_STEP)

        if not BoardRegistrationNumber(self.professional).is_completed:
            raise CannotSetStatusError(BOARD_VERIFICATION_NOT_APPROVED_YET)

        self.professional.active = True
        self.professional.save(update_fields=["active"])

        # Log da aprovação da etapa
        logger.info(
            "Etapa de validação aprovada: %s - Profissional ID: %s",
            self.description,
            self.professional.id,
        )

        email_context = PostRegistrationApprovedContext(
            button_url=format_professional_url(""),
        ).model_dump(mode="json")
        notification.send(
            sender=self,
            template_prefix="verification/post_registration_approved",
            email=self.professional.user.email,
            context=email_context,
            recipient=self.professional.user,
        )

    def set_rejected(self, professsional_review, request=None):
        # Save clinic data
        clinic_data = serializers.serialize("json", [self.professional.clinic])
        professsional_review.rejected_professional_data = clinic_data
        professsional_review.save()

        # Delete clinic data
        self.professional.clinic.delete()

        email_context = PostRegistrationRejectedContext(
            button_url=format_professional_url(""),
        ).model_dump(mode="json")
        notification.send(
            sender=self,
            template_prefix="verification/post_registration_rejected",
            email=self.professional.user.email,
            context=email_context,
            recipient=self.professional.user,
        )


class IntersectionalityData(VerificationStep):
    """
    Na etapa, pedimos que adicione os dados de interseccionalidade.
    """

    name = "add_intersectionality_data"
    url_path_to_submit = "/saude/cadastro-diversidade/"
    url_path_to_wait_completion = ""
    description = "3ª - Diversidade"

    @cached_property
    def is_completed(self):
        professional = self.professional
        intersectionality_fields = {
            "ethnic_group": bool(
                professional.ethnic_group_id or professional.other_ethnic_group
            ),
            "pronoun": bool(professional.pronoun_id or professional.other_pronoun),
            "sexual_orientation": bool(
                professional.sexual_orientation_id
                or professional.other_sexual_orientation
            ),
            "gender_identity": bool(
                professional.gender_identity_id or professional.other_gender_identity
            ),
        }
        return all(intersectionality_fields.values())

    @cached_property
    def is_submitted(self):
        return self.is_completed


class VerificationStepsService:
    def __init__(self, professional):
        self.professional = professional
        self.steps = [
            BoardRegistrationNumber(professional),
            EmailConfirmation(professional),
            IntersectionalityData(professional),
            PostRegistrationData(professional),
        ]

    def to_representation(self) -> dict:
        current_step = None
        steps_repr = {}

        for step in self.steps:
            if not step.is_completed and not current_step:
                current_step = step.name

            steps_repr[step.name] = step.to_representation()

        return {"current_step": current_step, "steps": steps_repr}

    def current_step(self):
        representation = self.to_representation()
        if not representation["current_step"]:
            return None
        return representation["steps"][representation["current_step"]]
