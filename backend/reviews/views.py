from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from businesses.models import Business

from .models import Review, ReviewFlag
from .serializers import ReviewCreateSerializer, ReviewFlagSerializer, ReviewSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    """
    GET /api/businesses/<business_id>/reviews/ — public, visible reviews only.
    POST /api/businesses/<business_id>/reviews/ — authenticated. One review
    per user per business; can't review a business you own.
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        return (
            ReviewCreateSerializer
            if self.request.method == "POST"
            else ReviewSerializer
        )

    def get_business(self):
        return get_object_or_404(Business, pk=self.kwargs["business_id"])

    def get_queryset(self):
        return Review.objects.filter(
            business=self.get_business(), is_removed=False
        ).select_related("user")

    def perform_create(self, serializer):
        business = self.get_business()

        if business.owner_id == self.request.user.id:
            raise ValidationError("You can't review a business you own.")

        if Review.objects.filter(business=business, user=self.request.user).exists():
            raise ValidationError("You've already reviewed this business.")

        serializer.save(business=business, user=self.request.user)


class ReviewDeleteView(generics.DestroyAPIView):
    """DELETE /api/reviews/<id>/ — a reviewer can remove their own review."""

    queryset = Review.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        review = super().get_object()
        if review.user_id != self.request.user.id:
            self.permission_denied(
                self.request, message="You can only delete your own review."
            )
        return review


class ReviewFlagView(APIView):
    """POST /api/reviews/<id>/flag/ — report a review for moderation."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk)

        if ReviewFlag.objects.filter(review=review, flagged_by=request.user).exists():
            return Response(
                {"detail": "You've already flagged this review."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ReviewFlagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(review=review, flagged_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
