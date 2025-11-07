from django.urls import path

from payment_cycle.views import PaymentCycleDuplicatedPaymentsAPIView

urlpatterns = [
    path('duplicated_payments/', PaymentCycleDuplicatedPaymentsAPIView.as_view()),
]
