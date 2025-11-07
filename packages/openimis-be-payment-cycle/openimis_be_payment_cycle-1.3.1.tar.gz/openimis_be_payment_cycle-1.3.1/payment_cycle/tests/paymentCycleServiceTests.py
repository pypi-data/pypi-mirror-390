import copy

from django.test import TestCase

from payment_cycle.models import PaymentCycle
from payment_cycle.tests.data import  service_add_payload, service_update_payload
from payment_cycle.services import PaymentCycleService
from core.test_helpers import LogInHelper


class PaymentCycleServiceTests(TestCase):
    user = None
    service = None

    test_benefit_plan = None
    test_individual_1 = None
    test_individual_2 = None
    test_beneficiary_1 = None
    test_beneficiary_2 = None
    test_payment_plan = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = LogInHelper().get_or_create_user_api()
        cls.service = PaymentCycleService(cls.user)
        cls.query_all = PaymentCycle.objects.filter(is_deleted=False)

    def test_create_payment_cycle(self):
        result = self.service.create(service_add_payload)
        self.assertTrue(result.get('success', False), result.get('detail', "No details provided"))
        uuid = result.get('data', {}).get('uuid', None)
        query = self.query_all.filter(uuid=uuid)
        self.assertEqual(query.count(), 1)


    def test_update_payment_cycle(self):
        result = self.service.create(service_add_payload)
        self.assertTrue(result.get('success', False), result.get('detail', "No details provided"))
        uuid = result.get('data', {}).get('uuid')
        update_payload = copy.deepcopy(service_update_payload)
        update_payload['id'] = uuid
        result = self.service.update(update_payload)
        self.assertTrue(result.get('success', False), result.get('detail', "No details provided"))
        query = self.query_all.filter(uuid=uuid)
        self.assertEqual(query.count(), 1)
        self.assertEqual(query.first().status, update_payload.get('status'))
