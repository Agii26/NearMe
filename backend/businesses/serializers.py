from rest_framework import serializers

from categories.serializers import CategorySerializer

from .models import Business


class BusinessListSerializer(serializers.ModelSerializer):
    """Used for search results — the grid card. Lean payload on purpose."""

    category = CategorySerializer(read_only=True)
    latitude = serializers.FloatField(source="location.y", read_only=True)
    longitude = serializers.FloatField(source="location.x", read_only=True)
    distance_km = serializers.SerializerMethodField()
    is_open_now = serializers.SerializerMethodField()

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
        ]

    def get_distance_km(self, obj):
        distance = getattr(obj, "distance", None)
        if distance is None:
            return None
        return round(distance.km, 2)

    def get_is_open_now(self, obj):
        return obj.is_open_now()


class BusinessDetailSerializer(serializers.ModelSerializer):
    """Used for the business profile page — the full read-only record."""

    category = CategorySerializer(read_only=True)
    latitude = serializers.FloatField(source="location.y", read_only=True)
    longitude = serializers.FloatField(source="location.x", read_only=True)
    is_open_now = serializers.SerializerMethodField()
    closes_at = serializers.SerializerMethodField()

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
            "is_open_now",
            "closes_at",
            "claimed",
        ]

    def get_is_open_now(self, obj):
        return obj.is_open_now()

    def get_closes_at(self, obj):
        return obj.next_close_time()
