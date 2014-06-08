from django.core.management.base import BaseCommand, CommandError
import django
from boxes.models import Box
import json
from django.utils.text import slugify
import os
DIR = os.path.dirname(__file__)

class Command(BaseCommand):
    help = 'Load sears shops'

    def handle(self, *args, **options):
        Box.objects.all().delete()

        raw = json.load(open(os.path.join(DIR,'edmunds.json')))
        stores = raw['dealerHolder']

        try:
            for store in stores:
                name = store['name']
                try:
                    box = Box(name=name, slug=slugify(name))
                    box.save()
                except django.db.utils.IntegrityError:
                    pass
                print(('kioto.io'+box.url()[:-1]+' ').rjust(60),box.name)
        except KeyboardInterrupt:
            print('\n  Operation interrupted')
