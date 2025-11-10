from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings

from lacrei_models.lacreiid.template_context_models import EmailConfirmationContext
from lacrei_models.notification.signals import notification


class AccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        user = context.pop("user")
        notification.send(
            sender=self,
            template_prefix=template_prefix,
            email=email,
            context=context,
            recipient=user,
        )

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        user = emailconfirmation.email_address.user
        is_professional = hasattr(user, "professional")
        if signup and is_professional:
            # Professional signup only receive a confirmation after the
            # board registration number is verified.
            return

        activate_url = self.get_email_confirmation_url(request, emailconfirmation)
        context = {
            "user": user,
        } | EmailConfirmationContext(
            activate_url=activate_url,
            receiver_name=user.first_name or "Usuário",
        ).model_dump(mode="json")

        if signup:
            email_template = "account/email/email_confirmation_signup"
        elif is_professional:
            email_template = "account/email_confirmation_professional"
        else:  # pragma: no cover
            raise NotImplementedError()  # this is unreachable
        self.send_mail(email_template, emailconfirmation.email_address.email, context)

    def send_confirmation_professional(self, user, request):
        from allauth.account.models import EmailAddress, EmailConfirmationHMAC

        email_address = EmailAddress.objects.get(user=user)
        confirmation = EmailConfirmationHMAC(email_address)
        confirmation.send(request=request, signup=False)

    def send_confirmation_user(self, email, request):
        from allauth.account.models import EmailAddress, EmailConfirmationHMAC

        email_address = EmailAddress.objects.get(email=email)

        user = email_address.user
        email_address.delete()
        email_address = EmailAddress.objects.create(
            user=user,
            email=email,
            verified=False,
            primary=True,
        )
        confirmation = EmailConfirmationHMAC(email_address)
        confirmation.send(request=request, signup=True)

    def get_email_verification_redirect_url(self, request, user, is_professional=False):
        """
        The URL to return to after successful e-mail confirmation.
        """
        return (
            settings.PROFESSIONAL_LOGIN_URL
            if is_professional
            else settings.USER_LOGIN_URL
        )
