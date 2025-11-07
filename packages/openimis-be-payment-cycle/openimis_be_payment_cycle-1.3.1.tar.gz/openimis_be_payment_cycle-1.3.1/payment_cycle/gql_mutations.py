import graphene
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext as _

from core.gql.gql_mutations.base_mutation import BaseHistoryModelCreateMutationMixin, BaseMutation, \
    BaseHistoryModelUpdateMutationMixin
from core.schema import OpenIMISMutation
from payment_cycle.apps import PaymentCycleConfig
from payment_cycle.models import PaymentCycle, PaymentCycleMutation
from payment_cycle.services import PaymentCycleService


class CreatePaymentCycleInput(OpenIMISMutation.Input):
    class PaymentCycleEnum(graphene.Enum):
        PENDING = PaymentCycle.PaymentCycleStatus.PENDING
        ACTIVE = PaymentCycle.PaymentCycleStatus.ACTIVE
        SUSPENDED = PaymentCycle.PaymentCycleStatus.SUSPENDED

    code = graphene.String(required=True)
    start_date = graphene.Date(required=True)
    end_date = graphene.Date(required=True)
    status = graphene.Field(PaymentCycleEnum, required=True)


class UpdatePaymentCycleInput(CreatePaymentCycleInput):
    id = graphene.UUID(required=True)


class CreatePaymentCycleMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = "payment_cycle"
    _mutation_class = "CreatePaymentCycleMutation"

    @classmethod
    def _validate_mutation(cls, user, **data):
        super()._validate_mutation(user, **data)
        if not user.has_perms(PaymentCycleConfig.gql_create_payment_cycle_perms):
            raise PermissionDenied(_("unauthorized"))

    @classmethod
    def _mutate(cls, user, **data):
        client_mutation_id = data.pop('client_mutation_id', None)
        data.pop('client_mutation_label', None)

        service = PaymentCycleService(user)
        if (PaymentCycleConfig.gql_check_payment_cycle and
                data["status"] == PaymentCycle.PaymentCycleStatus.ACTIVE):
            res = service.create_create_task(data)
        else:
            res = service.create(data)
            if client_mutation_id and res['success']:
                payment_cycle_id = res['data']['id']
                payment_cycle = PaymentCycle.objects.get(id=payment_cycle_id)
                PaymentCycleMutation.object_mutated(
                    user, client_mutation_id=client_mutation_id, payment_cycle=payment_cycle
                )
        return res if not res['success'] else None

    class Input(CreatePaymentCycleInput):
        pass


class UpdatePaymentCycleMutation(BaseHistoryModelUpdateMutationMixin, BaseMutation):
    _mutation_module = "payment_cycle"
    _mutation_class = "PaymentCycleMutation"
    _model = PaymentCycle

    @classmethod
    def _validate_mutation(cls, user, **data):
        super()._validate_mutation(user, **data)
        if not user.has_perms(PaymentCycleConfig.gql_update_payment_cycle_perms):
            raise PermissionDenied(_("unauthorized"))

    @classmethod
    def _mutate(cls, user, **data):
        client_mutation_id = data.pop('client_mutation_id', None)
        data.pop('client_mutation_label', None)

        service = PaymentCycleService(user)
        if PaymentCycleConfig.gql_check_payment_cycle:
            res = service.create_update_task(data)
        else:
            res = service.update(data)
        if client_mutation_id and res['success']:
            payment_cycle_id = data["id"]
            payment_cycle = PaymentCycle.objects.get(id=payment_cycle_id)
            PaymentCycleMutation.object_mutated(
                user, client_mutation_id=client_mutation_id, payment_cycle=payment_cycle
            )
        return res if not res['success'] else None

    class Input(UpdatePaymentCycleInput):
        pass
