import pycountry

from django.core.management.base import BaseCommand
from apps.common.models import Country



class Command(BaseCommand):
    help = 'Imports a list of countries from pycountry'

    def handle(self, *args, **options):
        created = 0
        for country in pycountry.countries:
            _, is_created = Country.objects.get_or_create(
                alpha_2=country.alpha_2,
                defaults={
                    'name': country.name,
                    'alpha_3': country.alpha_3,
                    'numeric': country.numeric,
                }
            )
            if is_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f'Country import complete. {created} countries added. {len(pycountry.countries)} countries in total.'))
