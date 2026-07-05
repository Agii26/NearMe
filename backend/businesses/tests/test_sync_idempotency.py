from unittest.mock import Mock, patch

from django.test import TestCase

from businesses.models import Business
from businesses.osm_sync import sync_businesses

FAKE_OVERPASS_RESPONSE = {
    "elements": [
        {
            "type": "node",
            "id": 111,
            "lat": 14.65,
            "lon": 121.05,
            "tags": {"amenity": "cafe", "name": "Better Days Café"},
        },
        {
            "type": "way",
            "id": 222,
            "center": {"lat": 14.60, "lon": 121.02},
            "tags": {"shop": "hardware", "name": "IronWorks Hardware"},
        },
        {
            "type": "node",
            "id": 333,
            "lat": 14.61,
            "lon": 121.03,
            "tags": {"amenity": "place_of_worship", "name": "Unmapped Tag Chapel"},
        },
        {
            "type": "node",
            "id": 444,
            "lat": 14.62,
            "lon": 121.04,
            "tags": {"shop": "bakery"},  # no name -> skipped
        },
    ]
}


def _mock_response():
    mock_resp = Mock()
    mock_resp.json.return_value = FAKE_OVERPASS_RESPONSE
    mock_resp.raise_for_status = Mock()
    return mock_resp


class SyncBusinessesIdempotencyTests(TestCase):
    @patch("businesses.osm_sync.requests.post")
    def test_first_run_creates_expected_records(self, mock_post):
        mock_post.return_value = _mock_response()

        counts = sync_businesses(
            bbox=(14.5, 121.0, 14.7, 121.1), api_url="https://example.test/interpreter"
        )

        self.assertEqual(counts["total_fetched"], 4)
        self.assertEqual(counts["created"], 2)
        self.assertEqual(counts["updated"], 0)
        self.assertEqual(counts["skipped"], 2)
        self.assertEqual(Business.objects.count(), 2)
        self.assertTrue(
            Business.objects.filter(osm_id="node/111", name="Better Days Café").exists()
        )
        self.assertTrue(
            Business.objects.filter(
                osm_id="way/222", name="IronWorks Hardware"
            ).exists()
        )

    @patch("businesses.osm_sync.requests.post")
    def test_second_run_updates_instead_of_duplicating(self, mock_post):
        mock_post.return_value = _mock_response()

        sync_businesses(
            bbox=(14.5, 121.0, 14.7, 121.1), api_url="https://example.test/interpreter"
        )
        first_run_count = Business.objects.count()

        # Re-run with identical data — this is the idempotency guarantee.
        counts = sync_businesses(
            bbox=(14.5, 121.0, 14.7, 121.1), api_url="https://example.test/interpreter"
        )

        self.assertEqual(Business.objects.count(), first_run_count)
        self.assertEqual(counts["created"], 0)
        self.assertEqual(counts["updated"], 2)

    @patch("businesses.osm_sync.requests.post")
    def test_rerun_picks_up_changed_fields(self, mock_post):
        mock_post.return_value = _mock_response()
        sync_businesses(
            bbox=(14.5, 121.0, 14.7, 121.1), api_url="https://example.test/interpreter"
        )

        updated_response = _mock_response()
        updated_response.json.return_value = {
            "elements": [
                {
                    "type": "node",
                    "id": 111,
                    "lat": 14.65,
                    "lon": 121.05,
                    "tags": {"amenity": "cafe", "name": "Better Days Café (Renamed)"},
                }
            ]
        }
        mock_post.return_value = updated_response
        sync_businesses(
            bbox=(14.5, 121.0, 14.7, 121.1), api_url="https://example.test/interpreter"
        )

        business = Business.objects.get(osm_id="node/111")
        self.assertEqual(business.name, "Better Days Café (Renamed)")
        self.assertEqual(Business.objects.filter(osm_id="node/111").count(), 1)
