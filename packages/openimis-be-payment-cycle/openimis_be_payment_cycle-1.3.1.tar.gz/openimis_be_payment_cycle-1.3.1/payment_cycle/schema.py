import graphene
import graphene_django_optimizer as gql_optimizer
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.utils.translation import gettext as _

from core.gql_queries import ValidationMessageGQLType
from core.schema import OrderedDjangoFilterConnectionField
from core.services import wait_for_mutation
from core.utils import append_validity_filter
from payment_cycle.apps import PaymentCycleConfig
from payment_cycle.gql_mutations import CreatePaymentCycleMutation, UpdatePaymentCycleMutation
from payment_cycle.gql_queries import PaymentCycleGQLType
from payment_cycle.models import PaymentCycle
from payment_cycle.validations import validate_payment_cycle_unique_code, validate_payment_cycle_whitespace_code


class Query(graphene.ObjectType):
    payment_cycle = OrderedDjangoFilterConnectionField(
        PaymentCycleGQLType,
        orderBy=graphene.List(of_type=graphene.String),
        dateValidFrom__Gte=graphene.DateTime(),
        dateValidTo__Lte=graphene.DateTime(),
        applyDefaultValidityFilter=graphene.Boolean(),
        search=graphene.String(),
        client_mutation_id=graphene.String(),
    )
    payment_cycle_code_validity = graphene.Field(
        ValidationMessageGQLType,
        code=graphene.String(required=True),
        description="Checks that the specified Benefit Plan code is valid"
    )

    def resolve_payment_cycle_code_validity(self, info, **kwargs):
        if not info.context.user.has_perms(PaymentCycleConfig.gql_query_payment_cycle_perms):
            raise PermissionDenied(_("unauthorized"))
        code = kwargs['code']
        errors = [*validate_payment_cycle_unique_code(code), *validate_payment_cycle_whitespace_code(code)]

        if errors:
            return ValidationMessageGQLType(False, error_message=errors[0]['message'])
        else:
            return ValidationMessageGQLType(True)


    def resolve_payment_cycle(self, info, **kwargs):
        filters = append_validity_filter(**kwargs)

        client_mutation_id = kwargs.get("client_mutation_id")
        if client_mutation_id:
            wait_for_mutation(client_mutation_id)
            filters.append(Q(mutations__mutation__client_mutation_id=client_mutation_id))

        Query._check_permissions(info.context.user, PaymentCycleConfig.gql_query_payment_cycle_perms)
        query = PaymentCycle.objects.filter(*filters)
        return gql_optimizer.query(query, info)

    @staticmethod
    def _check_permissions(user, perms):
        if type(user) is AnonymousUser or not user.id or not user.has_perms(perms):
            raise PermissionError("Unauthorized")


class Mutation(graphene.ObjectType):
    create_payment_cycle = CreatePaymentCycleMutation.Field()
    update_payment_cycle = UpdatePaymentCycleMutation.Field()
