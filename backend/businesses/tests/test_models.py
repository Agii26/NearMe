from datetime import datetime

from django.contrib.gis.geos import Point
from django.test import TestCase
from django.utils import timezone

from categories.models import Category
from businesses.models import Business


class IsOpenNowTests(TestCase):
    def setUp(self):
        self.category = Category.objects.get(slug="food-dining")

    def _business(self, hours):
        return Business.objects.create(
            name="Test Business",
            category=self.category,
            location=Point(121.05, 14.65),
            hours=hours,
        )

    def test_unknown_hours_returns_none(self):
        business = self._business(hours=None)
        self.assertIsNone(business.is_open_now())

    def test_explicitly_closed_today_returns_false(self):
        business = self._business(hours={"sun": []})
        moment = timezone.make_aware(datetime(2026, 7, 5, 14, 0))  # a Sunday
        self.assertFalse(business.is_open_now(at=moment))

    def test_within_open_span_returns_true(self):
        business = self._business(hours={"sun": [["09:00", "18:00"]]})
        moment = timezone.make_aware(datetime(2026, 7, 5, 14, 0))
        self.assertTrue(business.is_open_now(at=moment))

    def test_outside_open_span_returns_false(self):
        business = self._business(hours={"sun": [["09:00", "18:00"]]})
        moment = timezone.make_aware(datetime(2026, 7, 5, 20, 0))
        self.assertFalse(business.is_open_now(at=moment))

    def test_24_00_end_of_day_marker_does_not_crash_and_stays_open(self):
        # Regression test: strptime's %H rejects '24:00' outright. This must
        # be treated as end-of-day, not silently skipped as unparseable.
        business = self._business(hours={"sun": [["00:00", "24:00"]]})
        moment = timezone.make_aware(datetime(2026, 7, 5, 23, 45))
        self.assertTrue(business.is_open_now(at=moment))

    def test_overnight_span_crossing_midnight(self):
        business = self._business(hours={"sun": [["18:00", "02:00"]]})
        late_night = timezone.make_aware(datetime(2026, 7, 5, 23, 0))
        self.assertTrue(business.is_open_now(at=late_night))
        mid_afternoon = timezone.make_aware(datetime(2026, 7, 5, 15, 0))
        self.assertFalse(business.is_open_now(at=mid_afternoon))

    def test_next_close_time_reports_correct_end(self):
        business = self._business(hours={"sun": [["09:00", "18:00"]]})
        moment = timezone.make_aware(datetime(2026, 7, 5, 14, 0))
        self.assertEqual(business.next_close_time(at=moment), "18:00")
