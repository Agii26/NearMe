from django.urls import path

from reviews.views import ReviewListCreateView

from .views import (
    BusinessDetailView,
    BusinessSearchView,
    ClaimBusinessView,
    MyBusinessesView,
    MyClaimsView,
    PhotoUploadView,
)

urlpatterns = [
    path("search", BusinessSearchView.as_view(), name="business-search"),
    path("mine/", MyBusinessesView.as_view(), name="business-mine"),
    path("claims/mine/", MyClaimsView.as_view(), name="claim-mine"),
    path("<int:pk>/", BusinessDetailView.as_view(), name="business-detail"),
    path("<int:pk>/claim/", ClaimBusinessView.as_view(), name="business-claim"),
    path("<int:pk>/photos/", PhotoUploadView.as_view(), name="business-photo-upload"),
    path(
        "<int:business_id>/reviews/",
        ReviewListCreateView.as_view(),
        name="business-reviews",
    ),
]
