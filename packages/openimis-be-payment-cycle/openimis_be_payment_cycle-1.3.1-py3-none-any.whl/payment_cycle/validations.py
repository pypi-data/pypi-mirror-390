from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from core.validation import ObjectExistsValidationMixin, UniqueCodeValidationMixin, BaseModelValidation
from core.validation.stringFieldValidationMixin import StringFieldValidationMixin
from payment_cycle.models import PaymentCycle


class PaymentCycleValidation(BaseModelValidation,
                             UniqueCodeValidationMixin,
                             ObjectExistsValidationMixin,
                             StringFieldValidationMixin):
    OBJECT_TYPE = PaymentCycle

    @classmethod
    def validate_create(cls, user, **data):
        cls.validate_unique_code_name(data.get('code', None))

    @classmethod
    def validate_update(cls, user, **data):
        cls.validate_object_exists(data.get('id', None))
        code = data.get('code', None)
        id_ = data.get('id', None)

        if code:
            cls.validate_unique_code_name(code, id_)



def validate_payment_cycle_unique_code(code, uuid=None):
    try:
        PaymentCycleValidation().validate_unique_code_name(code, uuid)
        return []
    except ValidationError as e:
        return [{"message": _("payment_cycle.validation.payment_cycle.code_exists" % {
            'code': code
        })}]


def validate_payment_cycle_whitespace_code(code, uuid=None):
    try:
        PaymentCycleValidation().validate_empty_string(code)
        PaymentCycleValidation().validate_string_whitespace_end(code)
        PaymentCycleValidation().validate_string_whitespace_start(code)
        return []
    except ValidationError as e:
        return [{"message": _("payment_cycle.validation.payment_cycle.code_whitespace")}]

