import logging

from core.service_signals import ServiceSignalBindType
from core.signals import bind_service_signal
from payment_cycle.services import PaymentCycleService
from tasks_management.services import on_task_complete_service_handler

logger = logging.getLogger(__name__)


def bind_service_signals():
    bind_service_signal(
        'task_service.complete_task',
        on_task_complete_service_handler(PaymentCycleService),
        bind_type=ServiceSignalBindType.AFTER
    )

