from django.conf import settings
from django.core.management.base import BaseCommand

from milove.shop.models.user import UserInfo


class Command(BaseCommand):
    help = 'Calculate and dispense interests for all users.'

    def handle(self, *args, **options):
        annualized_return = settings.BALANCE_ANNUALIZED_RETURN / 100.0
        for info in UserInfo.objects.filter(balance__gt=0.0):
            info.increase_balance(info.balance * annualized_return / 365)
