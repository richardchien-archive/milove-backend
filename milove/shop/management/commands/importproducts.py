import os
import json
import random
import hashlib
import shutil

from django.core.management.base import BaseCommand
from django.utils import timezone

from milove.shop.models import *
from milove.shop.file_storage import storage


class Command(BaseCommand):
    help = 'Import normalized product json files.'

    def add_arguments(self, parser):
        parser.add_argument('-j', '--json-dir')
        parser.add_argument('-u', '--uploads-dir')

    def handle(self, *args, **options):
        prod_json_dir = options['json_dir']
        uploads_dir = options['uploads_dir']

        for file in os.listdir(prod_json_dir):
            with open(os.path.join(prod_json_dir, file), 'r',
                      encoding='utf8') as f:
                prod = json.loads(f.read())

            ignored_fields = ('id', 'published_dt', 'main_image', 'images',
                              'categories', 'attachments', 'brand')

            product = Product()

            # basic

            for key in prod.keys():
                if key not in ignored_fields:
                    setattr(product, key, prod[key])

            brand, _ = Brand.objects.get_or_create(name=prod['brand'])
            product.brand = brand
            product.save()

            # published and sold datetime

            product.published_dt = prod['published_dt'] + 'Z'
            product.save()
            # make sure the `published_dt` is a datetime object
            product.refresh_from_db()
            if product.sold:
                now = timezone.now()
                delta = now - product.published_dt
                product.sold_dt = now - timezone.timedelta(
                    days=random.randint(1, delta.days - 1))

            # attachments

            for att in prod['attachments']:
                attachment, _ = Attachment.objects.get_or_create(name=att)
                product.attachments.add(attachment)

            # categories

            while prod['categories']:
                lvl_1_cat, lvl_2_cat, lvl_3_cat, *prod['categories'] = prod[
                    'categories']
                lvl_1_cat_obj, _ = Category.objects.get_or_create(
                    name=lvl_1_cat, level=1)
                lvl_2_cat_obj, _ = Category.objects.get_or_create(
                    name=lvl_2_cat, super_category=lvl_1_cat_obj, level=2)
                lvl_3_cat_obj, _ = Category.objects.get_or_create(
                    name=lvl_3_cat, super_category=lvl_2_cat_obj, level=3)
                product.categories.add(lvl_1_cat_obj, lvl_2_cat_obj,
                                       lvl_3_cat_obj)

            # images

            counter = 1

            def move_image_file(p, image_file):
                image_file = image_file.replace('/', os.path.sep)
                filename, ext = os.path.splitext(image_file)
                date_str = p.published_dt.strftime('%Y%m%d')
                filename_hash = hashlib.md5()
                filename_hash.update(filename.encode('utf-8'))
                filename_hash.update(date_str.encode('utf-8'))
                new_dir = 'products/%s/' % p.pk
                os.makedirs(storage.path(new_dir), exist_ok=True)
                new_image_file = new_dir + '{}{:02d}-{}{}'.format(
                    date_str, counter,
                    filename_hash.hexdigest(),
                    ext
                )
                # os.rename(os.path.join(uploads_dir, image_file),
                #           storage.path(new_image_file))
                shutil.copyfile(os.path.join(uploads_dir, image_file),
                                storage.path(new_image_file))
                return new_image_file

            images = [prod['main_image']] + prod.get('images', [])
            for i, img in enumerate(images):
                images[i] = move_image_file(product, img[len('uploads/'):])
            product.main_image = images[0]
            for img in images[1:]:
                ProductImage.objects.create(
                    image=img,
                    product=product
                )

            product.save()
            self.stdout.write(
                self.style.SUCCESS('Product %s done.' % product.pk))

        self.stdout.write(self.style.SUCCESS('Successfully import products.'))
