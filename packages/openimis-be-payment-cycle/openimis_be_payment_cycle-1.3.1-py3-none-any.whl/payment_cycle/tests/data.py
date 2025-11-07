from core.datetimes.ad_datetime import datetime
from payment_cycle.models import PaymentCycle

service_add_payload = {
    'code': 'ELOO',
    'start_date': '2021-05-01',
    'end_date': '2021-06-01',
    'status': PaymentCycle.PaymentCycleStatus.PENDING,
}

service_update_payload = {
    'code': 'ELOO',
    'start_date': '2021-05-01',
    'end_date': '2021-06-01',
    'status': PaymentCycle.PaymentCycleStatus.ACTIVE,
}
