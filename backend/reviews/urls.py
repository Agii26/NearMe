from django.urls import path

from .views import ReviewDeleteView, ReviewFlagView

urlpatterns = [
    path("<int:pk>/", ReviewDeleteView.as_view(), name="review-delete"),
    path("<int:pk>/flag/", ReviewFlagView.as_view(), name="review-flag"),
]
