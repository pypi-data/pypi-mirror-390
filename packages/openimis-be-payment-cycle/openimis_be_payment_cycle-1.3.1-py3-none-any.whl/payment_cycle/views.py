import logging

from rest_framework import views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from core.utils import DefaultStorageFileHandler
from core.views import check_user_rights
from payment_cycle.apps import PaymentCycleConfig
from payment_cycle.services import PaymentCycleService

logger = logging.getLogger(__name__)


class PaymentCycleDuplicatedPaymentsAPIView(views.APIView):
    permission_classes = [check_user_rights(PaymentCycleConfig.gql_query_payment_cycle_perms, )]

    def get(self, request):
        try:
            payment_cycle = request.GET.get('payment_cycle_id')
            service = PaymentCycleService(request.user)
            in_memory_file = service.download_duplicates(payment_cycle)
            response = Response(headers={'Content-Disposition': f'attachment; filename="payments_duplicates.csv"'},
                                content_type='text/csv')
            response.content = in_memory_file.getvalue()
            return response
        except ValueError as exc:
            logger.error("Error while fetching duplicated payments", exc_info=exc)
            return Response({'success': False, 'error': str(exc)}, status=400)
        except Exception as exc:
            logger.error("Error while fetching duplicated payments", exc_info=exc)
            return Response({'success': False, 'error': str(exc)}, status=500)
