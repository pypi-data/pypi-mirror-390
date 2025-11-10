import uuid
from datetime import timedelta
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext as _
from notification.signals import notification

from lacrei_models.appointments.models import Appointment
from lacrei_models.lacreisaude.models import Professional
from lacrei_models.utils.models import BaseModel, HashedAutoField


class Bank(BaseModel):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    ispb = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        app_label = "payments"


class Payment(BaseModel):
    PENDING = "pending"
    PAYED = "payed"
    FAILED = "failed"
    PAYMENT_STATUS = [
        (PENDING, _("Pendente")),
        (PAYED, _("Pago")),
        (FAILED, _("Falhou")),
    ]
    CREDIT_CARD = "credit_card"
    PIX = "pix"
    PAYMENT_METHOD = [
        (CREDIT_CARD, _("Cartão de Crédito")),
        (PIX, _("PIX")),
    ]

    REFUND_STATUS = [
        ("none", _("Sem reembolso")),
        ("requested", _("Solicitado")),
        ("processing", _("Processando")),
        ("processed", _("Processado")),
        ("failed", _("Falhou")),
        ("no_refund", _("Sem direito a reembolso")),
    ]

    id = HashedAutoField(primary_key=True)
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name=_("Consulta"),
    )
    asaas_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("ID da Cobrança na Asaas"),
    )
    value = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal(0.00))],
        verbose_name=_("Valor da consulta"),
    )
    status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS,
        default=PENDING,
        verbose_name=_("Status do Pagamento"),
    )
    method = models.CharField(
        max_length=15,
        choices=PAYMENT_METHOD,
        default=CREDIT_CARD,
        verbose_name=_("Método do Pagamento"),
    )
    external_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("ID externo (ASAAS)"),
    )
    transferred_payment = models.BooleanField(default=False)

    class Meta:
        app_label = "payments"
        indexes = [
            models.Index(fields=["external_id"], name="payment_external_id_idx"),
            models.Index(
                fields=["status", "created_at"], name="payment_status_created_idx"
            ),
        ]

    external_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("ID do pagamento no Asaas"),
    )

    refund_status = models.CharField(
        max_length=20,
        choices=REFUND_STATUS,
        default="none",
        verbose_name=_("Status do Reembolso"),
    )
    refund_reason = models.TextField(
        blank=True, null=True, verbose_name=_("Motivo do reembolso")
    )
    refund_requested_at = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Data da solicitação do reembolso")
    )
    refund_requested_by = models.ForeignKey(
        "lacreiid.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="requested_refunds",
        verbose_name=_("Usuário que solicitou o reembolso"),
    )
    external_refund_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("ID do reembolso no Asaas"),
    )
    patient_refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Valor reembolsado ao paciente"),
    )
    professional_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Valor do profissional"),
    )
    lacrei_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Valor Lacrei"),
    )

    def pre_update_instance(self, *args, **kwargs):
        if self.pk:
            try:
                previous = Payment.objects.get(pk=self.pk)
                self._previous_status = previous.status
            except Payment.DoesNotExist:
                self._previous_status = None
        else:
            self._previous_status = None

    def _send_payment_confirmation_emails(self):
        """Envia emails de confirmação de pagamento para usuário e profissional."""
        from appointments.utils import AppointmentEmailContextBuilder

        # Envia email para o usuário
        context = AppointmentEmailContextBuilder(
            self.appointment
        ).build_context_to_user()
        notification.send(
            sender=self.__class__,
            template_prefix="appointments/user_appointment_particular_confirmation",
            email=self.appointment.user.email,
            context=context,
            recipient=self.appointment.user,
        )

        # Envia email para a pessoa profissional
        context = AppointmentEmailContextBuilder(
            self.appointment
        ).build_context_to_professional()
        context.update(
            {
                "payment_value": self.value,
                "payment_method": self.get_method_display(),
            }
        )
        notification.send(
            sender=self.__class__,
            template_prefix="appointments/professional_confirm_payment_sucess",
            email=self.appointment.professional.user.email,
            context=context,
            recipient=self.appointment.professional.user,
        )

    def post_create_instance(self, *args, **kwargs):
        # Envia confirmação se já nascer como PAYED
        if self.status == self.PAYED and self.appointment and self.appointment.user:
            self._send_payment_confirmation_emails()

    def post_update_instance(self, *args, **kwargs):
        changed_to_payed = (
            getattr(self, "_previous_status", None) != self.PAYED
            and self.status == self.PAYED
        )
        if changed_to_payed and self.appointment and self.appointment.user:
            self._send_payment_confirmation_emails()

    @property
    def can_be_refunded(self):
        return self.status == self.PAYED and self.refund_status in ["none", "failed"]

    @property
    def refund_deadline_passed(self):
        if not self.created_at:
            return False
        return timezone.now() > (self.created_at + timedelta(days=90))

    def __str__(self):
        return f"Payment {self.id} - {self.appointment} - R$ {self.value}"


class Customer(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    id_user = models.ForeignKey("lacreiid.User", on_delete=models.CASCADE)

    class Meta:
        app_label = "payments"


class BillingStatus(BaseModel):
    PENDING = "PENDING"
    RECEIVED = "RECEIVED"
    CONFIRMED = "CONFIRMED"
    OVERDUE = "OVERDUE"
    REFUNDED = "REFUNDED"
    RECEIVED_IN_CASH = "RECEIVED_IN_CASH"
    REFUND_REQUESTED = "REFUND_REQUESTED"
    REFUND_IN_PROGRESS = "REFUND_IN_PROGRESS"
    CHARGEBACK_REQUESTED = "CHARGEBACK_REQUESTED"
    CHARGEBACK_DISPUTE = "CHARGEBACK_DISPUTE"
    AWAITING_CHARGEBACK_REVERSAL = "AWAITING_CHARGEBACK_REVERSAL"
    DUNNING_REQUESTED = "DUNNING_REQUESTED"
    DUNNING_RECEIVED = "DUNNING_RECEIVED"
    AWAITING_RISK_ANALYSIS = "AWAITING_RISK_ANALYSIS"

    STATUS_CHOICES = [
        (PENDING, _("Pendente")),
        (RECEIVED, _("Recebido")),
        (CONFIRMED, _("Confirmado")),
        (OVERDUE, _("Vencido")),
        (REFUNDED, _("Reembolsado")),
        (RECEIVED_IN_CASH, _("Recebido em dinheiro")),
        (REFUND_REQUESTED, _("Reembolso solicitado")),
        (REFUND_IN_PROGRESS, _("Reembolso em andamento")),
        (CHARGEBACK_REQUESTED, _("Chargeback solicitado")),
        (CHARGEBACK_DISPUTE, _("Disputa de chargeback")),
        (AWAITING_CHARGEBACK_REVERSAL, _("Aguardando reversão de chargeback")),
        (DUNNING_REQUESTED, _("Cobrança judicial solicitada")),
        (DUNNING_RECEIVED, _("Cobrança judicial recebida")),
        (AWAITING_RISK_ANALYSIS, _("Aguardando análise de risco")),
    ]

    id = HashedAutoField(primary_key=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES)
    payment_id = models.ForeignKey("Payment", on_delete=models.CASCADE)

    def __str__(self):
        return f"BillingStatus {self.id} - {self.status}"

    class Meta:
        app_label = "payments"


@receiver(post_delete, sender=Customer)
def trigger_asaas_customer_delete(sender, instance, **kwargs):
    from payments.tasks import delete_customer_on_asaas

    delete_customer_on_asaas.delay(instance.id)


class PaymentsRelease(models.Model):
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="payment_transaction",
        verbose_name=_("Consulta"),
    )
    professional = models.ForeignKey(
        Professional,
        on_delete=models.CASCADE,
        related_name="professional_payment_transaction",
        verbose_name=_("Consulta"),
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)

    asaas_transfer_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "payments"


class IdempotencyKey(BaseModel):
    key = models.CharField(max_length=128, unique=True)
    appointment_id = models.CharField(max_length=64)
    method = models.CharField(max_length=15)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    response_status = models.IntegerField(null=True, blank=True)
    response_body = models.JSONField(null=True, blank=True)
    expires_at = models.DateTimeField()

    class Meta:
        app_label = "payments"
        indexes = [
            models.Index(fields=["expires_at"], name="idempotency_key_expires_idx"),
        ]

    @classmethod
    def is_valid(cls, key: str) -> bool:
        rec = cls.objects.filter(key=key).only("expires_at").first()
        return bool(rec and rec.expires_at > timezone.now())


class PaymentReprocess(BaseModel):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    FAILED = "failed"
    STATUS = [
        (PENDING, PENDING),
        (SCHEDULED, SCHEDULED),
        (COMPLETED, COMPLETED),
        (FAILED, FAILED),
    ]

    payment = models.ForeignKey(
        Payment, on_delete=models.CASCADE, related_name="reprocesses"
    )
    external_id = models.CharField(max_length=100, null=True, blank=True)
    attempt_count = models.IntegerField(default=0)
    last_error = models.TextField(null=True, blank=True)
    next_attempt_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS, default=PENDING)

    class Meta:
        app_label = "payments"
        indexes = [
            models.Index(
                fields=["status", "next_attempt_at"], name="reprocess_status_next_idx"
            ),
        ]


class AsaasWebhookLog(models.Model):
    """
    Modelo para registrar cada webhook recebido da Asaas, servindo como
    trilha de auditoria e controle de idempotência.
    """

    RECEIVED = "RECEIVED"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PROCESSED = "PROCESSED"
    IGNORED = "IGNORED"

    STATUS_CHOICES = [
        (RECEIVED, "Recebido"),
        (QUEUED, "Enfileirado"),
        (PROCESSING, "Processando"),
        (SUCCESS, "Sucesso"),
        (FAILED, "Falhou"),
        (PROCESSED, "Processado"),
        (IGNORED, "Ignorado"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_id = models.CharField(
        max_length=255, unique=True, help_text="ID do evento da Asaas para idempotência"
    )
    event_type = models.CharField(max_length=100, db_index=True)
    payload = models.JSONField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=RECEIVED, db_index=True
    )
    received_at = models.DateTimeField(auto_now_add=True)
    processing_log = models.TextField(
        blank=True, null=True, help_text="Log de erros ou observações do processamento."
    )

    class Meta:
        app_label = "payments"
        verbose_name = "Log de Webhook da Asaas"
        verbose_name_plural = "Logs de Webhooks da Asaas"
        ordering = ["-received_at"]

    def __str__(self):
        return f"{self.event_type} ({self.id}) - {self.status}"
