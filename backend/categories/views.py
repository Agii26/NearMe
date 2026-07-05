from rest_framework import generics

from .models import Category
from .serializers import CategorySerializer


class CategoryListView(generics.ListAPIView):
    """GET /api/categories/ — powers the filter chips on the search page."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None
