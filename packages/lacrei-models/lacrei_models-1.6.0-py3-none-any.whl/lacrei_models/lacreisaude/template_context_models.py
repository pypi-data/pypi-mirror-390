from datetime import datetime

from django.urls import reverse
from pydantic import HttpUrl

from lacrei_models.lacreiid.template_context_models import EmailConfirmationContext
from lacrei_models.utils.template_context_models import (
    WithBaseEmailContext,
    WithoutBaseEmailContext,
)


class EmailConfirmationProfessionalContext(EmailConfirmationContext):
    _template_prefix: str = "account/email_confirmation_professional"


class NewComplaintContext(WithoutBaseEmailContext):
    _template_prefix: str = "complaints/new_complaint"
    complaint__created_at: datetime
    complaint__id: str
    complaint_detail_url: HttpUrl

    @classmethod
    def _convert_from_pickled_content_to_this_model_args(
        self, pickled_context: dict
    ) -> dict:
        complaint = pickled_context.get("complaint", None)
        api_host = pickled_context.get("API_HOST", "")
        complaint_detail_url = f"{api_host}{reverse('admin:lacreisaude_complaint_change', args=[complaint.id])}"

        return {
            "complaint__created_at": complaint.created_at if complaint else None,
            "complaint__id": complaint.id if complaint else None,
            "complaint_detail_url": complaint_detail_url,
        }


class RequestBoardRegistrationNumberVerificationContext(WithoutBaseEmailContext):
    _template_prefix: str = (
        "request_verification/request_board_registration_number_verification"
    )
    professional__id: str
    professional__created_at: datetime
    professional__full_name: str
    professional__board_registration_number: str
    professional__profession__name: str
    professional__state__name: str
    step_name: str
    professional_detail_url: HttpUrl
    add_professional_review_url: HttpUrl

    @classmethod
    def _convert_from_pickled_content_to_this_model_args(
        self, pickled_context: dict
    ) -> dict:
        return {}  # pragma: no cover


class RequestBoardCertificationSelfieVerificationContext(WithoutBaseEmailContext):
    _template_prefix: str = (
        "request_verification/request_board_certification_selfie_verification"
    )
    professional__id: str
    professional__updated_at: datetime
    professional__full_name: str
    professional__board_registration_number: str
    professional__profession__name: str
    professional__state__name: str
    step_name: str
    professional_detail_url: HttpUrl
    add_professional_review_url: HttpUrl

    @classmethod
    def _convert_from_pickled_content_to_this_model_args(
        self, pickled_context: dict
    ) -> dict:
        return {}  # pragma: no cover


class BoardVerificationNumberRejectedContext(WithBaseEmailContext):
    _template_prefix: str = "verification/board_verification_number_rejected"

    @classmethod
    def _convert_from_pickled_content_to_this_model_args(
        self, pickled_context: dict
    ) -> dict:
        return {}


class PostRegistrationApprovedContext(WithBaseEmailContext):
    _template_prefix: str = "verification/post_registration_approved"
    button_url: HttpUrl

    @classmethod
    def _convert_from_pickled_content_to_this_model_args(
        self, pickled_context: dict
    ) -> dict:
        button_url = pickled_context.get("button_url", "")

        return {"button_url": button_url}


class PostRegistrationRejectedContext(WithBaseEmailContext):
    _template_prefix: str = "verification/post_registration_rejected"
    button_url: HttpUrl

    @classmethod
    def _convert_from_pickled_content_to_this_model_args(
        self, pickled_context: dict
    ) -> dict:
        button_url = pickled_context.get("button_url", "")

        return {"button_url": button_url}


class PostContactQuestionnaireUserContext(WithBaseEmailContext):
    _template_prefix: str = "questionnaire/post_contact_user_questionnaire"
    questionnaire_url: HttpUrl

    @classmethod
    def _convert_from_pickled_content_to_this_model_args(
        self, pickled_context: dict
    ) -> dict:
        """
        O coverage foi desabilitado nesse método porque
        ainda não foi implementada uma lógica para o envio do email questionnaire
        """
        questionnaire_url = pickled_context.get(
            "questionnaire_url", ""
        )  # pragma: no cover

        return {"questionnaire_url": questionnaire_url}  # pragma: no cover


class PostContactQuestionnaireProfessionalContext(WithBaseEmailContext):
    _template_prefix: str = "questionnaire/post_contact_professional_questionnaire"
    questionnaire_url: HttpUrl
    professional__first_name: str
    user__full_name: str

    @classmethod
    def _convert_from_pickled_content_to_this_model_args(
        self, pickled_context: dict
    ) -> dict:
        """
        O coverage foi desabilitado nesse método porque
        ainda não foi implementada uma lógica para o envio do email questionnaire
        """
        questionnaire_url = pickled_context.get("questionnaire_url", "")
        professional__first_name = pickled_context.get("professional__first_name", "")
        user__full_name = pickled_context.get("user__full_name", "")

        return {
            "questionnaire_url": questionnaire_url,
            "professional__first_name": professional__first_name,
            "user__full_name": user__full_name,
        }  # pragma: no cover


class PostAppointmentQuestionnaireUserContext(WithBaseEmailContext):
    _template_prefix: str = "questionnaire/post_appointment_user_questionnaire"
    questionnaire_url: HttpUrl
    user__first_name: str
    professional__full_name: str

    @classmethod
    def _convert_from_pickled_content_to_this_model_args(
        self, pickled_context: dict
    ) -> dict:
        """
        O coverage foi desabilitado nesse método porque
        ainda não foi implementada uma lógica para o envio do email questionnaire
        """
        questionnaire_url = pickled_context.get("questionnaire_url", "")
        user__first_name = pickled_context.get("user__first_name", "")
        professional__full_name = pickled_context.get("professional__full_name", "")

        return {
            "questionnaire_url": questionnaire_url,
            "user__first_name": user__first_name,
            "professional__full_name": professional__full_name,
        }  # pragma: no cover


class UserContactNoticeContext(WithBaseEmailContext):
    _template_prefix: str = "notice/user_contact_notice"
    user_name: str
    user_pronoun: str
    user_ethnicity: str
    user_gender_identity: str
    user_sexuality: str
    user_disabilities: str
    profile_image_src: str

    @classmethod
    def _convert_from_pickled_content_to_this_model_args(
        self, pickled_context: dict
    ) -> dict:  # pragma: no cover
        """
        O coverage foi desabilitado nesse método porque
        ainda não foi implementada uma lógica para o envio do email user_contact_notice
        """
        user_name = pickled_context.get("user_name", "")
        user_pronoun = pickled_context.get("user_pronoun", "")
        user_ethnicity = pickled_context.get("user_ethnicity", "")
        user_gender_identity = pickled_context.get("user_gender_identity", "")
        user_sexuality = pickled_context.get("user_sexuality", "")
        user_disabilities = pickled_context.get("user_disabilities", "")
        profile_image_src = pickled_context.get("profile_image_src", "")

        return {
            "user_name": user_name,
            "user_pronoun": user_pronoun,
            "user_ethnicity": user_ethnicity,
            "user_gender_identity": user_gender_identity,
            "user_sexuality": user_sexuality,
            "user_disabilities": user_disabilities,
            "profile_image_src": profile_image_src,
        }
