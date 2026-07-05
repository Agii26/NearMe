from django.urls import path

from .views import BusinessDetailView, BusinessSearchView

urlpatterns = [
    path("search", BusinessSearchView.as_view(), name="business-search"),
    path("<int:pk>/", BusinessDetailView.as_view(), name="business-detail"),
]
