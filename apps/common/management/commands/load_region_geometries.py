import json
import os

from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from django.core.management.base import BaseCommand

from apps.common.models import Region


class Command(BaseCommand):
    help = "Update region geometries from filtered_regions.json"

    def handle(self, *args, **options):
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "fixtures",
            "region_geometries.json",
        )

        try:
            with open(file_path) as file:
                regions_data = json.load(file)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR("Invalid JSON file"))
            return

        updated = 0
        skipped = 0
        polygon_count = 0

        for region_json in regions_data:
            country_code = region_json.get("iso_3166_2")
            geometry = region_json.get("geometry")

            if not (country_code and geometry):
                skipped += 1
                continue

            region = Region.objects.filter(code=country_code).first()
            if not region:
                self.stderr.write(
                    self.style.WARNING(f"Region not found: {country_code}")
                )
                skipped += 1
                continue

            geom = GEOSGeometry(json.dumps(geometry))
            if geom.geom_type == "Polygon":
                geom = MultiPolygon(geom)
                polygon_count += 1

            region.geometry = geom
            region.save()
            updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Update complete: {updated} regions updated, {skipped} skipped. {polygon_count} polygons converted to MultiPolygon."
            )
        )
