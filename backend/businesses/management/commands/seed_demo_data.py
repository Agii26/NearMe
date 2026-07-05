from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from categories.models import Category
from businesses.models import Business

DEMO_BUSINESSES = [
    {
        "name": "Better Days Café",
        "category_slug": "food-dining",
        "lat": 14.6507,
        "lng": 121.0494,
        "address": "42 Maginhawa St, Quezon City",
        "contact_phone": "0917 123 4567",
        "hours": {
            d: [["07:00", "21:00"]]
            for d in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        },
    },
    {
        "name": "Kusina ni Aling Nena",
        "category_slug": "food-dining",
        "lat": 14.6555,
        "lng": 121.0512,
        "address": "18 Matalino St, Quezon City",
        "contact_phone": "0918 222 3344",
        "hours": {
            d: [["10:00", "20:00"]] for d in ["mon", "tue", "wed", "thu", "fri", "sat"]
        },
    },
    {
        "name": "IronWorks Hardware",
        "category_slug": "retail",
        "lat": 14.6420,
        "lng": 121.0450,
        "address": "7 Kalayaan Ave, Quezon City",
        "contact_phone": "0917 555 7788",
        "hours": {
            d: [["08:00", "18:00"]] for d in ["mon", "tue", "wed", "thu", "fri", "sat"]
        },
    },
    {
        "name": "Casa Verde Plants",
        "category_slug": "retail",
        "lat": 14.6480,
        "lng": 121.0530,
        "address": "3 Malingap St, Quezon City",
        "contact_phone": "0919 888 1122",
        "hours": {
            d: [["09:00", "17:00"]] for d in ["tue", "wed", "thu", "fri", "sat", "sun"]
        },
    },
    {
        "name": "Glow Up Salon",
        "category_slug": "beauty-personal-care",
        "lat": 14.6530,
        "lng": 121.0470,
        "address": "55 Anonas St, Quezon City",
        "contact_phone": "0920 333 4455",
        "hours": {
            d: [["10:00", "19:00"]]
            for d in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        },
    },
    {
        "name": "QC Family Clinic",
        "category_slug": "health-wellness",
        "lat": 14.6460,
        "lng": 121.0480,
        "address": "21 Katipunan Ave, Quezon City",
        "contact_phone": "0917 999 0011",
        "hours": {d: [["08:00", "17:00"]] for d in ["mon", "tue", "wed", "thu", "fri"]},
    },
]


class Command(BaseCommand):
    help = (
        "Seeds a small set of realistic, hand-written demo businesses around "
        "Quezon City for local development and demoing, without needing a "
        "live Overpass API call. Idempotent, matches on name+category."
    )

    def handle(self, *args, **options):
        created, updated = 0, 0
        for entry in DEMO_BUSINESSES:
            category = Category.objects.get(slug=entry["category_slug"])
            _, was_created = Business.objects.update_or_create(
                name=entry["name"],
                category=category,
                osm_id=None,
                defaults={
                    "location": Point(entry["lng"], entry["lat"]),
                    "address": entry["address"],
                    "contact_phone": entry["contact_phone"],
                    "hours": entry["hours"],
                },
            )
            created += was_created
            updated += not was_created

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo data seeded: {created} created, {updated} updated."
            )
        )
