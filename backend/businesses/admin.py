from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from .models import Business


@admin.register(Business)
class BusinessAdmin(GISModelAdmin):
    list_display = ("name", "category", "claimed", "osm_id", "updated_at")
    list_filter = ("category", "claimed")
    search_fields = ("name", "address", "osm_id")
