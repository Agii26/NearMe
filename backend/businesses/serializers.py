from django.db.models import Avg
from rest_framework import serializers

from categories.serializers import CategorySerializer

from .models import Business, BusinessClaim, Media


class BusinessListSerializer(serializers.ModelSerializer):
    """Used for search results — the grid card. Lean payload on purpose."""

    category = CategorySerializer(read_only=True)
    latitude = serializers.FloatField(source="location.y", read_only=True)
    longitude = serializers.FloatField(source="location.x", read_only=True)
    distance_km = serializers.SerializerMethodField()
    is_open_now = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Business
        fields = [
            "id",
            "name",
            "category",
            "latitude",
            "longitude",
            "address",
            "distance_km",
            "is_open_now",
            "average_rating",
            "review_count",
        ]

    def get_distance_km(self, obj):
        distance = getattr(obj, "distance", None)
        if distance is None:
            return None
        return round(distance.km, 2)

    def get_is_open_now(self, obj):
        return obj.is_open_now()

    def get_average_rating(self, obj):
        avg = getattr(obj, "average_rating", None)
        return round(avg, 1) if avg is not None else None

    def get_review_count(self, obj):
        return getattr(obj, "review_count", 0)


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ["id", "image", "created_at"]


class BusinessDetailSerializer(serializers.ModelSerializer):
    """Used for the business profile page — the full read-only record."""

    category = CategorySerializer(read_only=True)
    latitude = serializers.FloatField(source="location.y", read_only=True)
    longitude = serializers.FloatField(source="location.x", read_only=True)
    is_open_now = serializers.SerializerMethodField()
    closes_at = serializers.SerializerMethodField()
    photos = MediaSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Business
        fields = [
            "id",
            "name",
            "category",
            "latitude",
            "longitude",
            "address",
            "contact_phone",
            "contact_email",
            "hours",
            "is_open_now",
            "closes_at",
            "claimed",
            "photos",
            "average_rating",
            "review_count",
            "is_owner",
        ]

    def get_is_owner(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.owner_id == request.user.id

    def get_is_open_now(self, obj):
        return obj.is_open_now()

    def get_closes_at(self, obj):
        return obj.next_close_time()

    def _visible_reviews(self, obj):
        return obj.reviews.filter(status="visible")

    def get_average_rating(self, obj):
        avg = self._visible_reviews(obj).aggregate(avg=Avg("rating"))["avg"]
        return round(avg, 1) if avg is not None else None

    def get_review_count(self, obj):
        return self._visible_reviews(obj).count()


class BusinessUpdateSerializer(serializers.ModelSerializer):
    """
    Used by the claiming owner's dashboard to edit their listing. Deliberately
    excludes osm_id/claimed/owner — those are never editable through this
    endpoint, only through the claim flow or the OSM sync.
    """

    class Meta:
        model = Business
        fields = [
            "name",
            "category",
            "address",
            "hours",
            "contact_phone",
            "contact_email",
        ]


class ClaimSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(source="business.name", read_only=True)

    class Meta:
        model = BusinessClaim
        fields = [
            "id",
            "business",
            "business_name",
            "status",
            "created_at",
            "reviewed_at",
        ]
        read_only_fields = ["status", "created_at", "reviewed_at"]
