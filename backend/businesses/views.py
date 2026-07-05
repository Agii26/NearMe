from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from .models import Business
from .serializers import BusinessDetailSerializer, BusinessListSerializer

DEFAULT_RADIUS_KM = 5
MAX_RADIUS_KM = 50


class BusinessSearchView(generics.ListAPIView):
    """
    GET /api/businesses/search?lat=&lng=&radius=&category=&q=

    lat/lng are required. radius is in kilometers (default 5, capped at 50).
    category is a Category slug. q does a case-insensitive name search.
    Results are always ordered nearest-first.
    """

    serializer_class = BusinessListSerializer

    def get_queryset(self):
        params = self.request.query_params

        lat = params.get("lat")
        lng = params.get("lng")
        if lat is None or lng is None:
            raise ValidationError("Both 'lat' and 'lng' query parameters are required.")

        try:
            lat = float(lat)
            lng = float(lng)
        except ValueError:
            raise ValidationError("'lat' and 'lng' must be numbers.")

        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            raise ValidationError("'lat'/'lng' are out of range.")

        radius_km = params.get("radius", DEFAULT_RADIUS_KM)
        try:
            radius_km = min(float(radius_km), MAX_RADIUS_KM)
        except ValueError:
            raise ValidationError("'radius' must be a number.")

        user_location = Point(lng, lat, srid=4326)

        queryset = (
            Business.objects.filter(
                location__distance_lte=(user_location, D(km=radius_km))
            )
            .annotate(distance=Distance("location", user_location))
            .select_related("category")
            .order_by("distance")
        )

        category_slug = params.get("category")
        if category_slug and category_slug != "all":
            queryset = queryset.filter(category__slug=category_slug)

        search_term = params.get("q")
        if search_term:
            queryset = queryset.filter(name__icontains=search_term)

        return queryset


class BusinessDetailView(generics.RetrieveAPIView):
    """GET /api/businesses/<id>/ — the read-only profile page."""

    queryset = Business.objects.select_related("category")
    serializer_class = BusinessDetailSerializer
