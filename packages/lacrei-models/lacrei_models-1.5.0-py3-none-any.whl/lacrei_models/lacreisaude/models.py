import calendar
from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal
from random import randint

from appointments.models import Appointment
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from lacreiid.models import NULLABLE, BaseProfile
from lacreisaude.constants import CONTACT_REQUEST_SMS_MESSAGE
from lacreisaude.managers import ContactRequestManager
from lacreisaude.services.verification import (
    BoardRegistrationNumber,
    PostRegistrationData,
    VerificationStepsService,
)
from lacreisaude.template_context_models import NewComplaintContext
from notification.signals import notification
from phonenumber_field.modelfields import PhoneNumberField
from utils.models import BaseModel, HashedAutoField, HashedFileName
from utils.validators import BRCPFValidator, OnlyAlphabeticValidator
from watson import search as watson

PROFILE_STATUS = [
    ("pending", _("Informações pendentes")),
    ("in_review", _("Em revisão")),
    ("rejected", _("Rejeitado")),
    ("approved", _("Aprovado")),
]

VERIFICATION_STEPS_MAP = {
    "board_registration_number": {
        "choice_description": "1º etapa - Numero de inscrição",
        "verification_step": BoardRegistrationNumber,
    },
    "post_registration_data": {
        "choice_description": "2º etapa - Pós cadastro",
        "verification_step": PostRegistrationData,
    },
}
VERIFICATION_STEPS_CHOICES = (
    (key, value["choice_description"]) for key, value in VERIFICATION_STEPS_MAP.items()
)


class Profession(BaseModel):
    name = models.CharField(max_length=100)
    search_synonym = models.CharField(max_length=256, default=None, **NULLABLE)

    class Meta:
        verbose_name = _("Profissão")
        verbose_name_plural = _("Profissões")
        app_label = "lacreisaude"

    def __str__(self):
        return self.name


class WaitingList(BaseModel):
    email = models.EmailField()
    profession = models.ForeignKey(Profession, on_delete=models.PROTECT)
    state = models.ForeignKey("address.State", on_delete=models.PROTECT)

    class Meta:
        verbose_name = _("Lista de espera")
        verbose_name_plural = _("Listas de espera")
        app_label = "lacreisaude"


class Professional(BaseProfile):
    CPF = "CPF"
    CNPJ = "CNPJ"
    EMAIL = "EMAIL"
    CELULAR = "PHONE"
    EVP = "EVP"
    tipo_chave = [
        (CPF, _("CPF")),
        (CNPJ, _("CNPJ")),
        (EMAIL, _("EMAIL")),
        (CELULAR, _("PHONE")),
        (EVP, _("EVP")),
    ]
    id = HashedAutoField(primary_key=True)
    user = models.OneToOneField("lacreiid.User", on_delete=models.PROTECT)
    full_name = models.CharField(
        max_length=200,
        verbose_name=_("Nome completo"),
        validators=[OnlyAlphabeticValidator()],
    )
    about_me = models.TextField(**NULLABLE, verbose_name=_("Sobre mim"))
    profile_status = models.CharField(
        max_length=30,
        choices=PROFILE_STATUS,
        default="pending",
        verbose_name=_("Status do perfil"),
    )
    state = models.ForeignKey(
        "address.State", on_delete=models.PROTECT, verbose_name=_("Estado")
    )
    active = models.BooleanField(
        default=False,
        help_text=(
            _("Define se o perfil está ativo e pode ser alterado pelos administradores")
        ),
        verbose_name=_("Ativo"),
    )
    published = models.BooleanField(
        default=True,
        help_text=(
            _(
                "Define se o perfil está publicado "
                "e pode ser alterado pelo próprio profissional"
            )
        ),
        verbose_name=_("Publicado"),
    )
    document_number = models.CharField(
        max_length=20, **NULLABLE, validators=[BRCPFValidator()], verbose_name=_("CPF")
    )
    profession = models.ForeignKey(
        Profession,
        related_name="professionals",
        on_delete=models.PROTECT,
        verbose_name=_("Profissão"),
    )
    search_synonym = models.CharField(max_length=256, default=None, **NULLABLE)
    board_registration_number = models.CharField(
        max_length=100, verbose_name=_("Número do registro do conselho")
    )
    accepted_privacy_document = models.BooleanField(
        default=False, verbose_name=_("Documento de privacidade aceito")
    )
    privacy_document = models.ForeignKey(
        "lacreiid.PrivacyDocument",
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        verbose_name=_("Documento de privacidade"),
    )
    safety_measures = models.CharField(
        max_length=1000,
        **NULLABLE,
        help_text=_("Medidas de segurança do Covid, por exemplo"),
        verbose_name=_("Medidas de segurança"),
    )
    specialty = models.CharField(
        **NULLABLE,
        max_length=250,
        help_text=_("Especialidade da pessoa profissional, como cardiologia"),
        verbose_name=_("Especialidade clínica"),
    )
    specialty_number_rqe = models.CharField(
        **NULLABLE,
        max_length=10,
        help_text=_("Registro de Qualificação de Especialidade (RQE)"),
        verbose_name=_("Registro de Qualificação de Especialidade (RQE)"),
    )
    board_certification_selfie = models.ImageField(
        **NULLABLE,
        upload_to=HashedFileName("board_certification_selfie"),
        verbose_name=_("Selfie do documento de registro do conselho"),
    )
    photo = models.ImageField(
        **NULLABLE,
        upload_to=HashedFileName("professional_photos"),
        verbose_name=_("Foto de perfil"),
    )
    photo_description = models.CharField(
        **NULLABLE,
        max_length=250,
        help_text=_("Descrição da foto de perfil para pessoas com deficiência visual"),
        verbose_name=_("Descrição da foto de perfil"),
    )
    google_calendar_credentials_json = models.JSONField(
        null=True,
        blank=True,
        help_text="Credenciais OAuth 2.0 para a API do Google Calendar.",
    )
    chave_pix = models.CharField(max_length=100, default=None, **NULLABLE)
    tipo_chave_pix = models.CharField(
        max_length=10,
        choices=tipo_chave,
        default=None,
        null=True,
        blank=True,
        verbose_name=_("tipo de chave pix"),
    )
    income_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        **NULLABLE,
        verbose_name=_("Renda/Faturamento Mensal"),
        help_text=_(
            "Renda mensal para PF ou faturamento mensal para PJ (obrigatório para criação)"
        ),
    )

    class Meta:
        verbose_name = _("Profissional")
        verbose_name_plural = _("Profissionais")
        app_label = "lacreisaude"

    def __str__(self):
        return self.full_name

    @property
    def current_step(self):
        current_step = VerificationStepsService(self).current_step()
        if not current_step:
            return None
        return current_step["description"], current_step["internal_message"]

    def get_all_times(self, type, duration):
        all_schedules = self.clinic.opening_schedules.filter(schedule_type=type)
        all_times = defaultdict(list)

        SHORT_TO_INDEX = {
            "mon": 0,
            "tue": 1,
            "wed": 2,
            "thu": 3,
            "fri": 4,
            "sat": 5,
            "sun": 6,
        }

        for schedule in all_schedules:
            weekday_raw = schedule.weekday

            if isinstance(weekday_raw, int) or (
                isinstance(weekday_raw, str) and weekday_raw.isdigit()
            ):
                weekday_index = int(weekday_raw)
            else:
                weekday_index = SHORT_TO_INDEX[weekday_raw.strip().lower()]

            current_time = datetime.combine(datetime.min, schedule.opening_time)
            closing_time = datetime.combine(datetime.min, schedule.closing_time)
            while current_time < closing_time:
                all_times[calendar.day_name[weekday_index]].append(current_time.time())
                current_time += duration

        return all_times

    def is_overlap(self, slot_start, slot_end, appointment_start, appointment_end):
        """
        Retorna True se houver sobreposição entre os intervalos de tempo.
        """
        return not (slot_end <= appointment_start or slot_start >= appointment_end)

    def get_available_times(self, initial_date, final_date, type):
        type_map = {
            Appointment.IN_PERSON: ClinicOpeningSchedule.PRESENTIAL,
            Appointment.ONLINE: ClinicOpeningSchedule.ONLINE,
        }
        schedule_type = type_map.get(type, type)
        duration = (
            timedelta(minutes=self.clinic.online_clinic_duration_minutes)
            if schedule_type == ClinicOpeningSchedule.ONLINE
            else timedelta(minutes=self.clinic.duration_minutes)
        )

        all_available_times = self.get_all_times(schedule_type, duration)
        available_times = defaultdict(list)
        dt = initial_date

        while dt <= final_date:
            appointments = self.appointments.filter(date__date=dt).exclude(
                status=Appointment.CANCELED
            )
            weekday_name = calendar.day_name[dt.weekday()]
            available_times[dt.strftime("%Y-%m-%d")] = all_available_times.get(
                weekday_name, []
            ).copy()
            for appointment in appointments:
                appointment_duration = (
                    timedelta(minutes=self.clinic.duration_minutes)
                    if appointment.type == Appointment.IN_PERSON
                    else timedelta(minutes=self.clinic.online_clinic_duration_minutes)
                )
                appointment_date = timezone.localtime(appointment.date)
                appointment_start = datetime.combine(dt, appointment_date.time())
                appointment_end = appointment_start + appointment_duration
                available_times[dt.strftime("%Y-%m-%d")] = [
                    time_slot
                    for time_slot in available_times[dt.strftime("%Y-%m-%d")]
                    if not self.is_overlap(
                        datetime.combine(dt, time_slot),
                        datetime.combine(dt, time_slot) + duration,
                        appointment_start,
                        appointment_end,
                    )
                ]
            dt += timedelta(days=1)

        return available_times


class Clinic(BaseModel):
    id = HashedAutoField(primary_key=True)
    professional = models.OneToOneField(
        Professional,
        on_delete=models.PROTECT,
        related_name="clinic",
        verbose_name=_("Profissional"),
    )
    is_presential_clinic = models.BooleanField(
        default=True, verbose_name=_("Clínica Presencial")
    )
    is_online_clinic = models.BooleanField(
        default=False, verbose_name=_("Clínica Online")
    )

    # Presential clinic fields
    name = models.CharField(
        max_length=100, **NULLABLE, verbose_name=_("Nome da Clínica")
    )
    zip_code = models.CharField(max_length=20, **NULLABLE, verbose_name=_("CEP"))
    registered_neighborhood = models.ForeignKey(
        "address.Neighborhood",
        on_delete=models.PROTECT,
        help_text=_("ID do bairro encontrado na API de busca de CEP"),
        **NULLABLE,
        verbose_name=_("ID do bairro"),
    )
    neighborhood = models.CharField(
        max_length=200,
        help_text=_("Nome do bairro"),
        **NULLABLE,
        verbose_name=_("Bairro"),
    )
    city = models.CharField(
        max_length=200,
        help_text=_("Nome da cidade"),
        **NULLABLE,
        verbose_name=_("Cidade"),
    )
    state = models.ForeignKey(
        "address.State", on_delete=models.PROTECT, verbose_name=_("Estado"), **NULLABLE
    )
    address = models.CharField(
        max_length=200,
        help_text=_("Endereço completo, incluindo número"),
        **NULLABLE,
        verbose_name=_("Endereço"),
    )
    address_line2 = models.CharField(
        max_length=200,
        help_text=_("Complemento do endereço"),
        **NULLABLE,
        verbose_name=_("Complemento"),
    )
    phone = PhoneNumberField(
        help_text=_("Telefone da clínica"),
        **NULLABLE,
        verbose_name=_("Telefone da clínica"),
    )
    phone_whatsapp = PhoneNumberField(
        help_text=_("Telefone WhatsApp"), **NULLABLE, verbose_name=_("Whatsapp")
    )
    consult_price = models.DecimalField(
        decimal_places=2,
        max_digits=9,
        validators=[MinValueValidator(Decimal(0.00))],
        help_text=_("Valor da Consulta"),
        **NULLABLE,
        verbose_name=_("Valor da Consulta"),
    )
    duration_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text=_("Duração em minutos da consulta"),
        **NULLABLE,
        verbose_name=_("Duração da consulta"),
    )
    accepts_insurance_providers = models.BooleanField(
        default=False,
        help_text=_("Aceita Convênios?"),
        verbose_name=_("Aceita Convênios"),
    )
    provides_accessibility_standards = models.BooleanField(
        default=False,
        help_text=_("Clínica possui acessibilidade?"),
        verbose_name=_("Clínica possui acessibilidade"),
    )

    # Online clinic fields
    online_clinic_phone = PhoneNumberField(
        help_text=_("Telefone da clínica"),
        **NULLABLE,
        verbose_name=_("Telefone da clínica"),
    )
    online_clinic_phone_whatsapp = PhoneNumberField(
        help_text=_("Telefone WhatsApp"), **NULLABLE, verbose_name="WhatsApp"
    )
    online_clinic_consult_price = models.DecimalField(
        decimal_places=2,
        max_digits=9,
        validators=[MinValueValidator(Decimal(0.00))],
        help_text=_("Valor da Consulta"),
        **NULLABLE,
        verbose_name=_("Valor da Consulta online"),
    )
    online_clinic_duration_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text=_("Duração em minutos da consulta"),
        **NULLABLE,
        verbose_name=_("Duração da consulta"),
    )
    online_clinic_accepts_insurance_providers = models.BooleanField(
        default=False,
        help_text=_("Aceita Convênios?"),
        verbose_name=_("Aceita Convênios"),
    )

    def __str__(self):
        return self.name or f"{self._meta.verbose_name} (id: {self.id})"

    class Meta:
        verbose_name = _("Clínica")
        verbose_name_plural = _("Clínicas")
        app_label = "lacreisaude"

    def post_create_instance(self, *args, **kwargs):
        watson.default_search_engine.update_obj_index(self.professional)

    def post_update_instance(self, *args, **kwargs):
        watson.default_search_engine.update_obj_index(self.professional)

    @property
    def full_address(self):
        parts = [
            self.address or "",
            self.address_line2 or "",
            self.neighborhood or "",
            self.city or "",
            self.state.code if self.state else "",
        ]
        return ", ".join(filter(None, parts)) or "Endereço não cadastrado"


class ClinicOpeningSchedule(BaseModel):
    ONLINE = "online"
    PRESENTIAL = "presential"
    SCHEDULE_TYPES = [
        (ONLINE, _("Online")),
        (PRESENTIAL, _("Presential")),
    ]
    SUN = "sun"
    MON = "mon"
    TUE = "tue"
    WED = "wed"
    THU = "thu"
    FRI = "fri"
    SAT = "sat"
    WEEKDAYS = [
        (SUN, _("Domingo")),
        (MON, _("Segunda-feira")),
        (TUE, _("Terça-feira")),
        (WED, _("Quarta-feira")),
        (THU, _("Quinta-feira")),
        (FRI, _("Sexta-feira")),
        (SAT, _("Sábado")),
    ]
    WEEKDAYS_MAP = {k: v for k, v in WEEKDAYS}
    id = HashedAutoField(primary_key=True)
    schedule_type = models.CharField(
        max_length=15,
        choices=SCHEDULE_TYPES,
        default="presential",
        verbose_name=_("Tipo de agendamento"),
    )
    weekday = models.CharField(
        max_length=3, choices=WEEKDAYS, verbose_name="Dia da semana"
    )
    clinic = models.ForeignKey(
        Clinic, on_delete=models.CASCADE, related_name="opening_schedules"
    )
    opening_time = models.TimeField(verbose_name="Horário de Abertura")
    closing_time = models.TimeField(verbose_name="Horário de fechamento")

    class Meta:
        verbose_name = _("Horário de abertura da clínica")
        verbose_name_plural = _("Horários de abertura da clínica")
        app_label = "lacreisaude"


class ProfessionalReview(BaseModel):
    id = HashedAutoField(primary_key=True)
    reviewed_by = models.ForeignKey(
        "lacreiid.User", on_delete=models.PROTECT, verbose_name=_("Revisado por")
    )
    professional = models.ForeignKey(
        Professional,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Profissional"),
    )
    professional_name = models.CharField(
        max_length=250, verbose_name=_("Nome do profissional")
    )
    profession = models.ForeignKey(
        Profession,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_("Profissão"),
    )
    internal_note = models.TextField(verbose_name=_("Nota interna"))
    status = models.CharField(
        max_length=20,
        choices=[
            ("approved", "Aprovado"),
            ("rejected", "Rejeitado"),
        ],
    )
    rejected_professional_data = models.JSONField(
        null=True,
        blank=True,
    )
    step = models.CharField(
        max_length=30,
        choices=VERIFICATION_STEPS_CHOICES,
        null=True,
        verbose_name=_("Etapas"),
    )

    def __str__(self):
        return self.professional_name

    class Meta:
        verbose_name = _("Revisão de profissional")
        verbose_name_plural = _("Revisão de profissionais")
        app_label = "lacreisaude"

    def pre_create_instance(self, *args, **kwargs):
        self.professional_name = self.professional.full_name

    def save(self, *args, **kwargs):
        self.request = kwargs.pop("request") if "request" in kwargs else None
        return super().save(*args, **kwargs)

    def post_create_instance(self, *args, **kwargs):
        VerificationStepClass = VERIFICATION_STEPS_MAP[self.step]["verification_step"]
        verification_step = VerificationStepClass(self.professional)

        # Set approved or rejected from the verification step in the service
        getattr(verification_step, f"set_{self.status}")(self, self.request)


class ContactRequest(BaseModel):
    id = HashedAutoField(primary_key=True)
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        help_text=_("Pessoa usuária solicitando o contato da profissional"),
        on_delete=models.deletion.PROTECT,
        verbose_name=_("Solicitante"),
    )
    requester_ip_address = models.GenericIPAddressField(verbose_name=_("Endereço IP"))
    requester_phone_number = PhoneNumberField(verbose_name=_("Telefone solicitante"))
    requester_user_agent = models.TextField(verbose_name=_("User Agent"))
    professional = models.ForeignKey(
        Professional, on_delete=models.deletion.PROTECT, verbose_name=_("Profissional")
    )
    validation_code = models.CharField(
        max_length=6, verbose_name=_("Código de validação")
    )
    code_confirmed = models.BooleanField(
        default=False, verbose_name=_("Código confirmado")
    )
    expires_at = models.DateTimeField(verbose_name=_("Expira em"))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("Criado em"))

    class Meta:
        verbose_name = _("Solicitação de Contato")
        verbose_name_plural = _("Solicitações de Contato")
        app_label = "lacreisaude"

    # Constants
    EXPIRES_IN_DAYS = 7

    # Manager
    objects = ContactRequestManager()

    def __str__(self) -> str:
        return f"{self.requester} -> {self.professional}"

    def pre_create_instance(self, *args, **kwargs):
        self.expires_at = timezone.now() + timedelta(
            days=ContactRequest.EXPIRES_IN_DAYS
        )
        self.validation_code = randint(100000, 999999)

    @property
    def sms_message(self):
        return CONTACT_REQUEST_SMS_MESSAGE.format(validation_code=self.validation_code)


class Complaint(BaseModel):
    id = HashedAutoField(primary_key=True)
    complaint_types = models.CharField(
        max_length=200, null=True, blank=True, verbose_name=_("Tipos de comportamento")
    )
    other_complaint_type = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Outros tipos de comportamento",
    )
    incident_date = models.DateField(verbose_name=_("Data do ocorrido"))
    incident_time = models.TimeField(verbose_name=_("Horário do ocorrido"))
    reported_by = models.ForeignKey(
        "lacreiid.User", on_delete=models.PROTECT, verbose_name=_("Reportado por")
    )
    description = models.TextField(verbose_name=_("Descrição do ocorrido"))
    professional = models.ForeignKey(
        Professional, on_delete=models.deletion.PROTECT, verbose_name=_("Profissional")
    )

    class Meta:
        verbose_name = _("Denúncia")
        verbose_name_plural = _("Denúncias")
        app_label = "lacreisaude"

    def post_create_instance(self, *args, **kwargs):
        context = NewComplaintContext(
            complaint__created_at=self.created_at,
            complaint__id=self.id,
            complaint_detail_url=f"{settings.API_HOST}{reverse('admin:lacreisaude_complaint_change', args=[self.id])}",
        ).model_dump(mode="json")

        notification.send(
            self,
            template_prefix="complaints/new_complaint",
            email=settings.COMPLAINT_EMAILS,
            context=context,
            recipient=None,
        )


class ProfessionalSubaccount(BaseModel):
    id = HashedAutoField(primary_key=True)
    professional = models.OneToOneField(
        "lacreisaude.Professional",
        on_delete=models.CASCADE,
        related_name="subaccount",
        verbose_name=_("Profissional"),
    )
    asaas_id = models.CharField(
        max_length=100, unique=True, verbose_name=_("ID no Asaas")
    )
    onboarding_url = models.URLField(
        max_length=500, **NULLABLE, verbose_name=_("URL de Onboarding de Documentos")
    )
    status_general = models.CharField(
        max_length=50, default="AWAITING_APPROVAL", verbose_name=_("Status Geral")
    )
    status_commercial_info = models.CharField(
        max_length=50,
        default="AWAITING_APPROVAL",
        verbose_name=_("Status Info. Comerciais"),
    )
    status_bank_account = models.CharField(
        max_length=50,
        default="AWAITING_APPROVAL",
        verbose_name=_("Status Conta Bancária"),
    )
    status_documentation = models.CharField(
        max_length=50,
        default="AWAITING_APPROVAL",
        verbose_name=_("Status Documentação"),
    )

    class Meta:
        verbose_name = _("Subconta de Profissional (Asaas)")
        verbose_name_plural = _("Subcontas de Profissionais (Asaas)")
        app_label = "lacreisaude"

    def __str__(self):
        return f"Subconta de {self.professional.full_name} ({self.asaas_id})"


class SubaccountDocument(BaseModel):
    """
    Armazena os arquivos de documento enviados para a verificação
    de uma subconta no Asaas.
    """

    id = HashedAutoField(primary_key=True)
    subaccount = models.ForeignKey(
        ProfessionalSubaccount,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name=_("Subconta"),
    )
    document_type = models.CharField(
        max_length=100,
        verbose_name=_("Tipo de Documento"),
        help_text=_("Ex: IDENTIFICATION, SOCIAL_CONTRACT"),
    )
    file = models.FileField(
        upload_to=HashedFileName("subaccount_documents"),
        verbose_name=_("Arquivo do Documento"),
    )
    asaas_id = models.CharField(
        max_length=100, unique=True, verbose_name=_("ID do Documento no Asaas")
    )
    status = models.CharField(
        max_length=50, default="pending", verbose_name=_("Status do Documento")
    )
    rejection_reason = models.TextField(
        **NULLABLE, verbose_name=_("Motivo da Rejeição")
    )

    class Meta:
        verbose_name = _("Documento de Subconta")
        verbose_name_plural = _("Documentos de Subcontas")
        app_label = "lacreisaude"

    def __str__(self):
        return f"Documento {self.document_type} de {self.subaccount.professional.full_name}"
