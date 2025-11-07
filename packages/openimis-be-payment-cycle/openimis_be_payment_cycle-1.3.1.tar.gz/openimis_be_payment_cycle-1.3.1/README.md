# openIMIS Backend payment_cycle reference module
This repository holds the files of the openIMIS Backend Payment Cycle reference module.
It is dedicated to be deployed as a module of [openimis-be_py](https://github.com/openimis/openimis-be_py).

## ORM mapping:
* payment_cycle_paymentcycle, payment_cycle_historicalpaymentcycle > Individual

## GraphQl Queries
* paymentCycle

## GraphQL Mutations - each mutation emits default signals and return standard error lists (cfr. openimis-be-core_py)
* processBenefitPlanPaymentCycle

## Services
- PaymentCycleService - Generic service containing workflow for payment cycle calculation
- BenefitPlanPaymentCycleService - Service customized for Benefit Plan payment cycle calculation

## Configuration options (can be changed via core.ModuleConfiguration)
* gql_query_payment_cycle_perms: required rights to query PaymentCycle (default: ["200001"])
* gql_create_payment_cycle_perms: required rights to create PaymentCycle (default: ["200002"])
* gql_update_payment_cycle_perms: required rights to update PaymentCycle (default: ["200003"])
* gql_delete_payment_cycle_perms: required rights to delete PaymentCycle (default: ["200004"])
* gql_mutation_process_payment_cycle_perms: required rights to call processBenefitPlanPaymentCycle GraphQL Mutation (default: ["200005"])


## openIMIS Modules Dependencies
- core
- social_protection
- contribution_plan
- calculation

# Payment Cycle Service
Payment cycle service specifies generic workflow for performing a calculation of periodical payments
for any king of business object connected to payment plans. This service includes a service specific 
to BenefitPlan objects. To trigger a calculation The service requires a user reference, year, and month.
Any additional keyword arguments can be passed to the ``process()`` method to be used in calculations.
```Python
result = BenefitPlanPaymentCycleService(user).process(year=year, month=month)
```
the result is a dict containing status of the operation, indicating if the operation completed successfully
or not, message and details of an error if occurred and any additional data that was returned from psecific implementation
of the services and calculation rules grouped by the id of main queryset entry (BenefitPlan id in this case).