from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from businesses.osm_sync import sync_businesses


class Command(BaseCommand):
    help = (
        "Pulls shops/amenities from OpenStreetMap's Overpass API within a "
        "bounding box and upserts them into the Business table. Safe to "
        "re-run — matches on osm_id, so it never creates duplicates."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--bbox",
            required=True,
            help=(
                "Bounding box as 'south,west,north,east' (decimal degrees). "
                "Example for Quezon City: --bbox=14.60,121.00,14.78,121.12"
            ),
        )

    def handle(self, *args, **options):
        raw_bbox = options["bbox"]
        try:
            bbox = tuple(float(v.strip()) for v in raw_bbox.split(","))
            if len(bbox) != 4:
                raise ValueError
        except ValueError:
            raise CommandError(
                "--bbox must be four comma-separated numbers: south,west,north,east"
            )

        self.stdout.write(f"Querying Overpass for bbox {bbox}...")
        counts = sync_businesses(bbox, settings.OVERPASS_API_URL)

        self.stdout.write(
            self.style.SUCCESS(
                f"Fetched {counts['total_fetched']} elements — "
                f"{counts['created']} created, {counts['updated']} updated, "
                f"{counts['skipped']} skipped (no name/category/coords)."
            )
        )
