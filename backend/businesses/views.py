from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Business, BusinessClaim, Media
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    BusinessDetailSerializer,
    BusinessListSerializer,
    BusinessUpdateSerializer,
    ClaimSerializer,
    MediaSerializer,
)

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


class BusinessDetailView(generics.RetrieveUpdateAPIView):
    """
    GET /api/businesses/<id>/ — the public, read-only profile page (anyone).
    PATCH /api/businesses/<id>/ — dashboard edits (claiming owner only).
    """

    queryset = Business.objects.select_related("category")
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return BusinessUpdateSerializer
        return BusinessDetailSerializer


class MyBusinessesView(generics.ListAPIView):
    """GET /api/businesses/mine/ — businesses the authenticated user owns."""

    serializer_class = BusinessDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Business.objects.filter(owner=self.request.user).select_related(
            "category"
        )


class ClaimBusinessView(APIView):
    """
    POST /api/businesses/<id>/claim/ — the authenticated user requests
    ownership of an unclaimed listing. Goes into the pending queue; nothing
    changes on the business itself until a claim is approved in the admin.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            business = Business.objects.get(pk=pk)
        except Business.DoesNotExist:
            return Response(
                {"detail": "Business not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if business.claimed:
            return Response(
                {"detail": "This business has already been claimed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing = BusinessClaim.objects.filter(
            business=business, user=request.user, status=BusinessClaim.PENDING
        ).first()
        if existing:
            return Response(
                {"detail": "You already have a pending claim on this business."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        claim = BusinessClaim.objects.create(business=business, user=request.user)
        return Response(ClaimSerializer(claim).data, status=status.HTTP_201_CREATED)


class MyClaimsView(generics.ListAPIView):
    """GET /api/businesses/claims/mine/ — the authenticated user's claim history and status."""

    serializer_class = ClaimSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BusinessClaim.objects.filter(user=self.request.user).select_related(
            "business"
        )


class PhotoUploadView(APIView):
    """POST /api/businesses/<id>/photos/ — multipart image upload, owner only."""

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request, pk):
        try:
            business = Business.objects.get(pk=pk)
        except Business.DoesNotExist:
            return Response(
                {"detail": "Business not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if business.owner_id != request.user.id:
            return Response(
                {"detail": "Only the claiming owner can upload photos."},
                status=status.HTTP_403_FORBIDDEN,
            )

        image = request.data.get("image")
        if not image:
            return Response(
                {"detail": "'image' file is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        media = Media.objects.create(
            business=business, uploaded_by=request.user, image=image
        )
        return Response(MediaSerializer(media).data, status=status.HTTP_201_CREATED)
