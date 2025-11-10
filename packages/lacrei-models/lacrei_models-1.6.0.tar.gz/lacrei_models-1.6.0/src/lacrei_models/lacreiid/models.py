from allauth.account.models import EmailAddress
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _
from phonenumber_field.modelfields import PhoneNumberField

from lacrei_models.lacreiid.managers import UserManager
from lacrei_models.utils.models import (
    NULLABLE,
    BaseModel,
    HashedAutoField,
    HashedFileName,
)
from lacrei_models.utils.validators import OnlyAlphabeticValidator


class User(AbstractUser, BaseModel):
    USER = "user"
    PROFESSIONAL = "professional"
    LOGGED_AS_CHOICES = [(USER, _("Usuário")), (PROFESSIONAL, _("Profissional"))]
    id = HashedAutoField(primary_key=True)
    logged_as = models.CharField(
        max_length=12,
        choices=LOGGED_AS_CHOICES,
        null=True,
        blank=True,
        help_text=_("Indica se o usuário está logado como Usuário ou Profissional"),
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(
        max_length=150, blank=False, validators=[OnlyAlphabeticValidator()]
    )
    last_name = models.CharField(
        max_length=150, blank=False, validators=[OnlyAlphabeticValidator()]
    )
    birth_date = models.DateField(**NULLABLE)
    is_18_years_old_or_more = models.BooleanField(**NULLABLE)
    last_login = models.DateTimeField(auto_now_add=True)
    email_verified = models.BooleanField(default=False)

    accepted_privacy_document = models.BooleanField(default=False)
    privacy_document = models.ForeignKey(
        "lacreiid.PrivacyDocument", on_delete=models.PROTECT, null=True, blank=False
    )
    newsletter_subscribed = models.BooleanField(default=True)

    phone = PhoneNumberField(null=True, blank=True)
    phone_verified = models.BooleanField(default=False)
    phone_verification_token = models.CharField(max_length=6, **NULLABLE)
    phone_verification_token_expires_at = models.DateTimeField(**NULLABLE)

    objects = UserManager()
    username = None
    date_joined = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("Pessoa Usuária")
        verbose_name_plural = _("Pessoas Usuárias")
        app_label = "lacreiid"

    def post_create_instance(self, *args, **kwargs):
        self.profile = Profile.objects.create(user=self)


class IntersectionalityBadge(models.Model):
    badge = models.ImageField(
        null=True,
        upload_to=HashedFileName("intersectionality_badges"),
        verbose_name=_("Selo de interseccionalidade"),
    )
    position_order = models.PositiveIntegerField(null=True, unique=True)

    class Meta:
        abstract = True


class DisabilityType(IntersectionalityBadge, BaseModel):
    name = models.CharField(max_length=100, blank=False)

    class Meta:
        verbose_name = _("Deficiência")
        verbose_name_plural = _("Deficiências")
        ordering = ["position_order"]
        app_label = "lacreiid"

    def __str__(self):
        return self.name


class SexualOrientation(IntersectionalityBadge, BaseModel):
    name = models.CharField(max_length=100, blank=False)

    class Meta:
        verbose_name = _("Orientação sexual")
        verbose_name_plural = _("Orientações sexuais")
        ordering = ["position_order"]
        app_label = "lacreiid"

    def __str__(self):
        return self.name


class GenderIdentity(IntersectionalityBadge, BaseModel):
    name = models.CharField(max_length=100, blank=False)

    class Meta:
        verbose_name = _("Identidade de gênero")
        verbose_name_plural = _("Identidades de gênero")
        ordering = ["position_order"]
        app_label = "lacreiid"

    def __str__(self):
        return self.name


class EthnicGroup(IntersectionalityBadge, BaseModel):
    name = models.CharField(max_length=100, blank=False)

    class Meta:
        verbose_name = _("Grupo étnico")
        verbose_name_plural = _("Grupos étnicos")
        ordering = ["position_order"]
        app_label = "lacreiid"

    def __str__(self):
        return self.name


class Pronoun(IntersectionalityBadge, BaseModel):
    article = models.CharField(max_length=1, blank=False)
    pronoun = models.CharField(max_length=50, blank=False)

    class Meta:
        verbose_name = _("Pronome")
        verbose_name_plural = _("Pronomes")
        ordering = ["position_order"]
        app_label = "lacreiid"

    def __str__(self):
        return f"{self.article}/{self.pronoun}"


class PrivacyDocument(BaseModel):
    privacy_policy = models.URLField()
    terms_of_use = models.URLField()
    profile_type = models.CharField(
        max_length=20,
        choices=[("lacreiid", _("Lacrei ID")), ("lacreisaude", _("Lacrei Saúde"))],
    )

    class Meta:
        verbose_name = _("Termo de uso e privacidade")
        verbose_name_plural = _("Termos de uso e privacidade")
        app_label = "lacreiid"

    def __str__(self):
        return f"{self.id} - {self.profile_type} - {self.created_at}"


class BaseProfile(BaseModel):
    ethnic_group = models.ForeignKey(
        EthnicGroup,
        on_delete=models.PROTECT,
        **NULLABLE,
        verbose_name=_("Grupo Étnico"),
    )
    gender_identity = models.ForeignKey(
        GenderIdentity,
        on_delete=models.PROTECT,
        **NULLABLE,
        verbose_name=_("Identidade de Gênero"),
    )
    sexual_orientation = models.ForeignKey(
        SexualOrientation,
        on_delete=models.PROTECT,
        **NULLABLE,
        verbose_name=_("Orientação Sexual"),
    )
    pronoun = models.ForeignKey(
        Pronoun, on_delete=models.PROTECT, **NULLABLE, verbose_name=_("Pronome")
    )
    disability_types = models.ManyToManyField(
        DisabilityType, blank=True, verbose_name=_("Tipos de deficiência")
    )

    other_ethnic_group = models.CharField(
        max_length=100, **NULLABLE, verbose_name=_("Outro Grupo Étnico")
    )
    other_gender_identity = models.CharField(
        max_length=100, **NULLABLE, verbose_name=_("Outra Identidade de Gênero")
    )
    other_sexual_orientation = models.CharField(
        max_length=100, **NULLABLE, verbose_name=_("Outra Orientação Sexual")
    )
    other_pronoun = models.CharField(
        max_length=100, **NULLABLE, verbose_name=_("Outro Pronome")
    )
    other_disability_types = models.CharField(
        max_length=100, **NULLABLE, verbose_name=_("Outro Tipos de deficiência")
    )
    other_article = models.CharField(
        max_length=1, **NULLABLE, verbose_name=_("Outro Artigo")
    )

    @property
    def display_ethnic_group(self):
        return self.other_ethnic_group or getattr(self.ethnic_group, "name", None)

    @property
    def display_gender_identity(self):
        return self.other_gender_identity or getattr(self.gender_identity, "name", None)

    @property
    def display_sexual_orientation(self):
        return self.other_sexual_orientation or getattr(
            self.sexual_orientation, "name", None
        )

    @property
    def display_pronoun(self):
        return self.other_pronoun or getattr(self.pronoun, "pronoun", None)

    @property
    def display_article(self):
        return self.other_article or getattr(self.pronoun, "article", None)

    @property
    def display_disability_types(self):
        disability_list = list(self.disability_types.values_list("name", flat=True))
        if self.other_disability_types:
            disability_list.append(self.other_disability_types)
        return ", ".join(disability_list) if disability_list else None

    class Meta:
        abstract = True


class Profile(BaseProfile):
    id = HashedAutoField(primary_key=True)
    user = models.OneToOneField(
        User, on_delete=models.PROTECT, verbose_name=_("Lacrei ID")
    )
    completed = models.BooleanField(
        default=False,
        verbose_name=_("Perfil completo"),
    )
    photo = models.ImageField(
        null=True,
        upload_to=HashedFileName("profile_photos"),
        verbose_name=_("Foto de perfil"),
    )
    photo_description = models.TextField(
        null=True, blank=True, help_text=_("Descrição da foto")
    )

    def __str__(self):
        return self.user.first_name

    class Meta:
        verbose_name = _("Perfil")
        verbose_name_plural = _("Perfis")
        app_label = "lacreiid"

    def save(self, *args, **kwargs):
        self.completed = all(
            [
                (self.ethnic_group_id or self.other_ethnic_group),
                (self.gender_identity_id or self.other_gender_identity),
                (self.sexual_orientation_id or self.other_sexual_orientation),
                (self.pronoun_id or (self.other_article and self.other_pronoun)),
                (self.disability_types.exists() or self.other_disability_types),
            ]
        )
        super().save(*args, **kwargs)


class CustomEmailAddress(EmailAddress):
    @classmethod
    def get_email_address_by_email(cls, email):
        try:
            email_record = cls.objects.get(email=email)
            return {
                "email": email_record.email,
                "user_id": email_record.user_id,
            }
        except cls.DoesNotExist:
            return None

    class Meta:
        proxy = True
        app_label = "lacreiid"
