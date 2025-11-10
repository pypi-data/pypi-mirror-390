from django.db.models import Manager


class ContactRequestManager(Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("professional", "requester")
