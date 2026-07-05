from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
    path("api/categories/", include("categories.urls")),
    path("api/businesses/", include("businesses.urls")),
]
