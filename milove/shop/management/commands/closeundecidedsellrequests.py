from django.core.management.base import BaseCommand
from django.utils import timezone

from milove.shop.models.sell_request import SellRequest


class Command(BaseCommand):
    help = 'Close undecided sell requests ' \
           'that have been valuated for over 2 weeks.'

    def handle(self, *args, **options):
        for sell_request in SellRequest.objects.filter(
                status=SellRequest.STATUS_VALUATED,
                valuated_dt__lt=timezone.now() - timezone.timedelta(weeks=2)):
            sell_request.status = SellRequest.STATUS_CLOSED
            sell_request.save()
