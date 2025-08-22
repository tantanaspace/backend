import pycountry

from django.core.management.base import BaseCommand
from apps.common.models import Country, Region


class Command(BaseCommand):
    help = 'Imports regions (subdivisions) from pycountry'

    def handle(self, *args, **options):        
        created = 0

        for subdivision in pycountry.subdivisions:
            try:
                country = Country.objects.get(alpha_2=subdivision.country_code)
            except Country.DoesNotExist:
                continue

            _, is_created = Region.objects.get_or_create(
                code=subdivision.code,
                defaults={
                    'name': subdivision.name,
                    'country': country,
                }
            )

            if is_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f'Region import complete. {created} regions added. {len(pycountry.subdivisions)} regions in total.'))
