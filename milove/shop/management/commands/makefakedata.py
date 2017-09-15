import json
import random
import string

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.test import Client

from milove.shop.models import *


def product_fill_in_serial_code_and_so_on():
    locations = list(ProductLocation.objects.all())
    authentication_methods = list(AuthenticationMethod.objects.all())
    for product in Product.objects.all():
        product.location = random.choice(locations)
        num = random.randint(0, 4)
        auth_methods = set()
        for _ in range(num):
            auth_methods.add(random.choice(authentication_methods))
        product.authentication_methods = auth_methods
        product.purchase_year = random.randint(2013, 2017)
        product.serial_code = ''.join(
            random.choice(string.ascii_uppercase + string.digits)
            for _ in range(12)
        )
        product.save()


def make_fake_orders(user, client):
    products = list(Product.objects.filter(sold=False))
    selected_prods = set(random.choices(products, k=30))
    addresses = list(Address.objects.filter(user=user))
    for prod in selected_prods:
        payload = {
            "products": [prod.pk],
            "shipping_address": random.choice(addresses).pk,
            "comment": '' if random.randint(0, 1) == 1 else 'Comment content',
            # "coupon": 'ABC'
        }
        client.post('/api/orders/', content_type='application/json',
                    data=json.dumps(payload))

    orders = list(Order.objects.filter(user=user))
    for order in random.choices(orders, k=5):
        client.put('/api/orders/%s/cancellation/' % order.pk)


def make_fake_sell_requests(user, client):
    brands = list(Brand.objects.all())
    categories = list(Category.objects.filter(level=3))
    for _ in range(random.randint(10, 30)):
        payload = {
            "brand": random.choice(brands).name,
            "category": str(random.choice(categories)),
            "name": "Some name %s" % random.randint(1, 999),
            "size": random.choice(['Small', 'Large', 'Medium', 'Micro']),
            "condition": random.choice(['九成新，只有少许磨损', '充新，仅试背']),
            "purchase_year": str(random.randint(2013, 2017)),
            "original_price": float(random.randint(600, 3000)),
            "attachments": random.choice(['小票', '无', '原包装、购买卡片']),
            "description": "blahblah 描述信息 %s" % random.randint(1, 999),
            "image_paths": []
        }
        client.post('/api/sell_requests/', content_type='application/json',
                    data=json.dumps(payload))

    sellrequests = list(SellRequest.objects.filter(user=user))
    for sell in random.choices(sellrequests, k=5):
        client.put('/api/sell_requests/%s/cancellation/' % sell.pk)


class Command(BaseCommand):
    help = 'Make fake data for Order, SellRequest and some other models.'

    def add_arguments(self, parser):
        parser.add_argument('-u', '--user')
        parser.add_argument('-p', '--password')

    def handle(self, *args, **options):
        self.stdout.write('Faking products\'s info...')
        product_fill_in_serial_code_and_so_on()

        user = get_user_model().objects.get(username=options['user'])

        client = Client()
        client.login(username=options['user'], password=options['password'])

        self.stdout.write('Faking orders...')
        make_fake_orders(user, client)

        self.stdout.write('Faking sell requests...')
        make_fake_sell_requests(user, client)

        self.stdout.write(self.style.SUCCESS('Successfully made fake data.'))
