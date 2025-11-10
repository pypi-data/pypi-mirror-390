from lacreiid.template_context_models import (
    AccountDeletedContext,
    EmailConfirmationSignupContext,
    PasswordResetContext,
)
from lacreisaude.template_context_models import (
    BoardVerificationNumberRejectedContext,
    EmailConfirmationProfessionalContext,
    NewComplaintContext,
    PostRegistrationApprovedContext,
    PostRegistrationRejectedContext,
    RequestBoardCertificationSelfieVerificationContext,
    RequestBoardRegistrationNumberVerificationContext,
)
from utils.template_context_models import BaseTemplateContext, WithBaseEmailContext

_PYDANTIC_MODELS_FROM_LACREIID = (
    AccountDeletedContext,
    EmailConfirmationProfessionalContext,
    EmailConfirmationSignupContext,
    PasswordResetContext,
)
_PYDANTIC_MODELS_FROM_LACREISAUDE = (
    NewComplaintContext,
    RequestBoardRegistrationNumberVerificationContext,
    RequestBoardCertificationSelfieVerificationContext,
    BoardVerificationNumberRejectedContext,
    PostRegistrationApprovedContext,
    PostRegistrationRejectedContext,
)
_ALL_PYDANTIC_MODELS = (
    *_PYDANTIC_MODELS_FROM_LACREIID,
    *_PYDANTIC_MODELS_FROM_LACREISAUDE,
)


TEMPLATE_PREFIX_TO_PYDANTIC_MODEL: dict[str, BaseTemplateContext] = {
    getattr(model._template_prefix, "default", model._template_prefix): model
    for model in _ALL_PYDANTIC_MODELS
}

TEMPLATE_PREFIX_HAS_BASE_EMAIL_CONTEXT: dict[str, bool] = {
    getattr(model._template_prefix, "default", model._template_prefix): issubclass(
        model, WithBaseEmailContext
    )
    for model in _ALL_PYDANTIC_MODELS
}
