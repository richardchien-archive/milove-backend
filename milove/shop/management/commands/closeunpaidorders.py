from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from milove.shop.models.order import Order


class Command(BaseCommand):
    help = 'Close unpaid orders that have been created for over 30 minutes.'

    def handle(self, *args, **options):
        for order in Order.objects.filter(
                status=Order.STATUS_UNPAID,
                created_dt__lt=timezone.now() - timezone.timedelta(
                    seconds=settings.ORDER_TIMEOUT)):
            order.status = Order.STATUS_CLOSED
            order.save()
