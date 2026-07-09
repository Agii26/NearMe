from django.contrib import admin
from django.db.models import Count

from .models import Review, ReviewFlag


class FlaggedFilter(admin.SimpleListFilter):
    title = "flagged"
    parameter_name = "flagged"

    def lookups(self, request, model_admin):
        return [("yes", "Has flags")]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.annotate(flag_count=Count("flags")).filter(flag_count__gt=0)
        return queryset


@admin.action(description="Remove selected reviews")
def remove_reviews(modeladmin, request, queryset):
    queryset.update(is_removed=True)


@admin.action(description="Restore selected reviews")
def restore_reviews(modeladmin, request, queryset):
    queryset.update(is_removed=False)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "business",
        "user",
        "rating",
        "is_removed",
        "flag_count",
        "created_at",
    )
    list_filter = ("is_removed", "rating", FlaggedFilter)
    search_fields = ("business__name", "user__username", "text")
    actions = [remove_reviews, restore_reviews]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(flag_count=Count("flags"))

    @admin.display(description="Flags", ordering="flag_count")
    def flag_count(self, obj):
        return obj.flag_count


@admin.register(ReviewFlag)
class ReviewFlagAdmin(admin.ModelAdmin):
    list_display = ("review", "flagged_by", "reason", "created_at")
