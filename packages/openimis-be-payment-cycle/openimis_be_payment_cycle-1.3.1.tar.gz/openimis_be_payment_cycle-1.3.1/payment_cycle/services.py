import pandas as pd
from io import BytesIO

from core.services import BaseService
from core.signals import register_service_signal
from payment_cycle.apps import PaymentCycleConfig
from payment_cycle.models import PaymentCycle
from payroll.models import BenefitConsumption, Payroll
from payment_cycle.validations import PaymentCycleValidation
from tasks_management.services import UpdateCheckerLogicServiceMixin, CreateCheckerLogicServiceMixin


class PaymentCycleService(BaseService, UpdateCheckerLogicServiceMixin, CreateCheckerLogicServiceMixin):
    OBJECT_TYPE = PaymentCycle

    def __init__(self, user, validation_class=PaymentCycleValidation):
        super().__init__(user, validation_class)

    @register_service_signal('payment_cycle_service.create')
    def create(self, obj_data):
        return super().create(obj_data)

    @register_service_signal('payment_cycle_service.update')
    def update(self, obj_data):
        return super().update(obj_data)

    @register_service_signal('payment_cycle_service.delete')
    def delete(self, obj_data):
        return super().delete(obj_data)

    @register_service_signal('payment_cycle_service.download')
    def download_duplicates(self, payment_cycle_id) -> BytesIO:
        payrolls = self._resolve_payrolls(payment_cycle_id)
        bc_qs = self._get_duplicated_benefit_consumption_qs(payrolls)
        df = pd.DataFrame.from_records(bc_qs.values(*PaymentCycleConfig.payment_cycle_benefits_field_mapping.keys()))
        df.rename(columns=PaymentCycleConfig.payment_cycle_benefits_field_mapping, inplace=True)

        in_memory_file = BytesIO()
        # BytesIO is duck-typed as a file object, so it can be passed to df.to_csv
        # noinspection PyTypeChecker
        df.to_csv(in_memory_file, index=False)
        return in_memory_file

    def _get_duplicated_benefit_consumption_qs(self, payrolls):
        qs = BenefitConsumption.objects.filter(
            payrollbenefitconsumption__payroll__id__in=payrolls,
            json_ext__contains={'duplicated': 'duplicated'},
            is_deleted=False
        ).order_by('individual__last_name', 'individual__first_name')
        if not qs.exists():
            raise ValueError('payment_cycle_service.validation.no_duplicated_payments_for_this_cycle')
        return qs

    def _resolve_payrolls(self, payment_cycle_id):
        if not payment_cycle_id:
            raise ValueError('payment_cycle_service.validation.payment_cycle_id_required')
        payrolls = Payroll.objects.filter(payment_cycle__id=payment_cycle_id, is_deleted=False)
        if not payrolls:
            raise ValueError('payment_cycle_service.validation.payroll_not_found')
        return payrolls.values_list('id', flat=True)
