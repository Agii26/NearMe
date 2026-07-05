from django.db import migrations

CATEGORIES = [
    ("Food & Dining", "food-dining", "ti-tools-kitchen-2"),
    ("Grocery", "grocery", "ti-shopping-cart"),
    ("Retail", "retail", "ti-building-store"),
    ("Health & Wellness", "health-wellness", "ti-stethoscope"),
    ("Beauty & Personal Care", "beauty-personal-care", "ti-scissors"),
    ("Automotive", "automotive", "ti-car"),
    ("Home Services", "home-services", "ti-tool"),
    ("Professional Services", "professional-services", "ti-briefcase"),
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model("categories", "Category")
    for name, slug, icon in CATEGORIES:
        Category.objects.update_or_create(slug=slug, defaults={"name": name, "icon": icon})


def remove_categories(apps, schema_editor):
    Category = apps.get_model("categories", "Category")
    Category.objects.filter(slug__in=[slug for _, slug, _ in CATEGORIES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_categories, remove_categories),
    ]
