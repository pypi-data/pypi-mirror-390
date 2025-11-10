from lacrei_models.appointments.models import Appointment
from lacrei_models.lacreisaude.models import Professional
from lacrei_models.payments.models import Payment


class AppointmentEmailContextBuilder:
    def __init__(self, appointment: Appointment):
        self.appointment = appointment

    def build_context_to_professional(self) -> dict:
        professional = self.appointment.professional
        user = self.appointment.user
        profile = user.profile
        agreement = self.appointment.agreement

        try:
            clinic_address = professional.clinic.address
            appointment_duration = (
                professional.clinic.duration_minutes
                if self.appointment.type == "in_person"
                else professional.clinic.online_clinic_duration_minutes
            )
        except Professional.clinic.RelatedObjectDoesNotExist:
            clinic_address = "Clínica não cadastrada"
            appointment_duration = 60  # Duração padrão em minutos

        context = {
            "receiver_name": professional.full_name,
            "fullname": f"{user.first_name} {user.last_name}",
            "photo": profile.photo.url if profile.photo else None,
            "appointment_date": (
                self.appointment.date.isoformat() if self.appointment.date else None
            ),
            "appointment_type": self.appointment.type,
            "appointment_type_display": self.appointment.get_type_display(),
            "user_pronoun": profile.display_pronoun or "Pronome não cadastrado",
            "user_gender_identity": profile.display_gender_identity
            or "Identidade de gênero não cadastrada",
            "user_sexuality": profile.display_sexual_orientation
            or "Orientação sexual não cadastrada",
            "professional_profession": professional.profession.name,
            "clinic_address": clinic_address,
            "agreement_name": agreement.name if agreement else None,
            "registration_number": agreement.registration_number if agreement else None,
            "appointment_duration": appointment_duration,
            "to_user": False,
        }

        # Adiciona informações de pagamento para consultas particulares
        if self.appointment.agreement is None:
            payment = self.appointment.payments.filter(status=Payment.PAYED).last()
            context["payment_method"] = (
                payment.get_method_display()
                if payment
                else "Nenhum pagamento realizado"
            )
            context["payment_value"] = payment.value if payment else 0.00

        return context

    def build_context_to_user(self) -> dict:
        professional = self.appointment.professional
        agreement = self.appointment.agreement
        payment = self.appointment.payments.filter(status=Payment.PAYED).last()
        clinic = getattr(professional, "clinic", None)

        # Duração da consulta
        if clinic:
            appointment_duration = (
                clinic.duration_minutes
                if self.appointment.type == "in_person"
                else clinic.online_clinic_duration_minutes
            )
        else:
            appointment_duration = 60  # Duração padrão em minutos

        context = {
            "receiver_name": f"{self.appointment.user.first_name} {self.appointment.user.last_name}",
            "fullname": professional.full_name,
            "photo": professional.photo.url if professional.photo else None,
            "professional_profession": professional.profession.name,
            "appointment_date": (
                self.appointment.date.isoformat() if self.appointment.date else None
            ),
            "appointment_type": self.appointment.type,
            "appointment_type_display": self.appointment.get_type_display(),
            "agreement_name": agreement.name if agreement else None,
            "registration_number": agreement.registration_number if agreement else None,
            "appointment_duration": appointment_duration,
            "to_user": True,
            # Dados REAIS de diversidade do PROFISSIONAL (acessados corretamente)
            "user_gender_identity": getattr(
                professional, "display_gender_identity", None
            )
            or "Não informado",
            "user_sexuality": getattr(professional, "display_sexual_orientation", None)
            or "Não informado",
            "user_ethnicgroup": getattr(professional, "display_ethnic_group", None)
            or "Não informado",
            "user_pronoun": getattr(professional, "display_pronoun", None)
            or "Não informado",
        }

        # Adiciona o endereço da clínica apenas para consultas presenciais
        if self.appointment.type == "in_person":
            context["clinic_address"] = (
                clinic.full_address if clinic else "Clínica não cadastrada"
            )
        if self.appointment.agreement is None:
            context["payment_method"] = (
                payment.get_method_display()
                if payment
                else "Nenhum pagamento realizado"
            )
            context["payment_value"] = payment.value if payment else 0.00

        return context
