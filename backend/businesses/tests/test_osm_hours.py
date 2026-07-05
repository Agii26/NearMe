from django.test import SimpleTestCase

from businesses.osm_hours import parse_opening_hours


class ParseOpeningHoursTests(SimpleTestCase):
    def test_simple_weekday_range(self):
        result = parse_opening_hours("Mo-Fr 09:00-18:00")
        for day in ["mon", "tue", "wed", "thu", "fri"]:
            self.assertEqual(result[day], [["09:00", "18:00"]])
        self.assertNotIn("sat", result)
        self.assertNotIn("sun", result)

    def test_multiple_rules_separated_by_semicolon(self):
        result = parse_opening_hours("Mo-Fr 09:00-18:00; Sa 09:00-13:00")
        self.assertEqual(result["fri"], [["09:00", "18:00"]])
        self.assertEqual(result["sat"], [["09:00", "13:00"]])
        self.assertNotIn("sun", result)

    def test_explicit_closed_day(self):
        result = parse_opening_hours("Mo-Sa 09:00-18:00; Su off")
        self.assertEqual(result["sun"], [])

    def test_comma_separated_days(self):
        result = parse_opening_hours("Mo,We,Fr 10:00-14:00")
        self.assertEqual(result["mon"], [["10:00", "14:00"]])
        self.assertEqual(result["wed"], [["10:00", "14:00"]])
        self.assertEqual(result["fri"], [["10:00", "14:00"]])
        self.assertNotIn("tue", result)

    def test_split_shift_with_lunch_break(self):
        result = parse_opening_hours("Mo-Fr 09:00-12:00,13:00-18:00")
        self.assertEqual(result["mon"], [["09:00", "12:00"], ["13:00", "18:00"]])

    def test_24_7(self):
        result = parse_opening_hours("24/7")
        self.assertEqual(result["mon"], [["00:00", "24:00"]])
        self.assertEqual(result["sun"], [["00:00", "24:00"]])

    def test_empty_or_none_returns_none(self):
        self.assertIsNone(parse_opening_hours(""))
        self.assertIsNone(parse_opening_hours(None))
        self.assertIsNone(parse_opening_hours("   "))

    def test_unparseable_syntax_returns_none_gracefully(self):
        # Real OSM tags can include holiday/seasonal syntax this parser
        # deliberately doesn't support — it must fail closed, not guess.
        self.assertIsNone(parse_opening_hours('Mo-Fr 09:00-18:00 || "by appointment"'))
        self.assertIsNone(parse_opening_hours("PH off"))
        self.assertIsNone(parse_opening_hours("sunrise-sunset"))

    def test_wraparound_day_range_not_supported(self):
        # Fr-Mo would wrap across the week boundary — out of scope, must fail closed.
        self.assertIsNone(parse_opening_hours("Fr-Mo 20:00-02:00"))
