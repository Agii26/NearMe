from datetime import datetime, time

from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils import timezone

from categories.models import Category

DAY_KEYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


class Business(models.Model):
    """
    A business listing. Rows with a populated `osm_id` originated from the
    OpenStreetMap sync job (see businesses/management/commands/sync_osm_businesses.py)
    and are unclaimed until an owner claims them in Phase 2.
    """

    osm_id = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        unique=True,
        help_text="OSM element id, e.g. 'node/123456'. Null for non-OSM-sourced rows.",
    )
    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="businesses",
    )
    location = gis_models.PointField(geography=True, spatial_index=True)
    address = models.CharField(max_length=500, blank=True)

    # Structured hours: {"mon": [["09:00", "18:00"]], "tue": [], ...}
    # An empty list for a day means closed that day. A missing key or null
    # top-level value means hours are unknown (never claim "closed" when we
    # simply don't know).
    hours = models.JSONField(null=True, blank=True)
    raw_hours_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="Original OSM opening_hours tag, kept even when parsing fails.",
    )

    contact_phone = models.CharField(max_length=50, blank=True)
    contact_email = models.EmailField(blank=True)

    claimed = models.BooleanField(default=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="claimed_businesses",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["osm_id"])]

    def __str__(self):
        return self.name

    @staticmethod
    def _parse_time(value):
        """
        '09:00' -> time(9,0). '24:00' is a valid OSM end-of-day marker that
        Python's %H (0-23) rejects, so it's special-cased to the last
        microsecond of the day rather than raising.
        """
        if value == "24:00":
            return time(23, 59, 59, 999999)
        return datetime.strptime(value, "%H:%M").time()

    def is_open_now(self, at=None):
        """
        Returns True/False, or None if hours are unknown/unparsed.
        `at` defaults to the current time (UTC-naive local time is out of
        scope for Phase 1 — timezone handling per-listing is a later
        refinement once businesses span multiple timezones).
        """
        if not self.hours:
            return None

        moment = at or timezone.localtime(timezone.now())
        day_key = DAY_KEYS[moment.weekday()]
        spans = self.hours.get(day_key)
        if spans is None:
            return None
        if not spans:
            return False

        current = moment.time()
        for start_str, end_str in spans:
            try:
                start = self._parse_time(start_str)
                end = self._parse_time(end_str)
            except (ValueError, TypeError):
                continue
            if start <= end:
                if start <= current <= end:
                    return True
            else:
                # Overnight span, e.g. 18:00–02:00
                if current >= start or current <= end:
                    return True
        return False

    def next_close_time(self, at=None):
        """Returns the 'HH:MM' close time for the current open span, if open now."""
        if not self.hours:
            return None
        moment = at or timezone.localtime(timezone.now())
        day_key = DAY_KEYS[moment.weekday()]
        spans = self.hours.get(day_key) or []
        current = moment.time()
        for start_str, end_str in spans:
            try:
                start = self._parse_time(start_str)
                end = self._parse_time(end_str)
            except (ValueError, TypeError):
                continue
            if start <= current <= end or (
                start > end and (current >= start or current <= end)
            ):
                return end_str
        return None
