from django.core.exceptions import ValidationError


class CannotSetStatusError(ValidationError):
    """
    Exception used when a transition can't be completed, like set_approved.
    """


class VerificatoinStepAlreadyApproved(CannotSetStatusError):
    pass


class VerificationStepConflict(CannotSetStatusError):
    pass
