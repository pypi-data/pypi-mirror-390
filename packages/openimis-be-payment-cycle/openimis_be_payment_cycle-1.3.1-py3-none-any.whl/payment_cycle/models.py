from django.contrib.contenttypes.models import ContentType
from django.db import models

from gettext import gettext as _

from core.models import HistoryModel, ObjectMutation, UUIDModel, MutationLog
from core.fields import DateField


class PaymentCycle(HistoryModel):
    class PaymentCycleStatus(models.TextChoices):
        PENDING = 'PENDING', _('PENDING')
        ACTIVE = 'ACTIVE', _('ACTIVE')
        SUSPENDED = 'SUSPENDED', _('SUSPENDED')

    code = models.CharField(max_length=255, blank=False, null=False)
    start_date = DateField(blank=False, null=False)
    end_date = DateField(blank=False, null=False)
    status = models.CharField(max_length=255, choices=PaymentCycleStatus.choices, default=PaymentCycleStatus.PENDING)
    type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING, blank=True, null=True, unique=False)

    def __str__(self):
        return f'Payment Cycle {self.code}: from {self.start_date} to {self.end_date}'


class PaymentCycleMutation(UUIDModel, ObjectMutation):
    payment_cycle = models.ForeignKey(PaymentCycle, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(
        MutationLog, models.DO_NOTHING, related_name='payment_cycle')
