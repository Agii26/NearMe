from django.urls import path

from .views import ReviewFlagView, ReviewUpdateDeleteView

urlpatterns = [
    path("<int:pk>/", ReviewUpdateDeleteView.as_view(), name="review-update-delete"),
    path("<int:pk>/flag/", ReviewFlagView.as_view(), name="review-flag"),
]
