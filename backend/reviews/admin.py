from django.contrib import admin

from .models import Review, ReviewFlag


@admin.action(description="Restore selected reviews (mark visible)")
def restore_reviews(modeladmin, request, queryset):
    for review in queryset:
        review.restore()


@admin.action(description="Remove selected reviews permanently")
def remove_reviews(modeladmin, request, queryset):
    for review in queryset:
        review.remove()


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("business", "user", "rating", "status", "flag_count", "created_at")
    list_filter = ("status", "rating")
    search_fields = ("business__name", "user__username", "text")
    actions = [restore_reviews, remove_reviews]

    @admin.display(description="Flags")
    def flag_count(self, obj):
        return obj.flags.count()


@admin.register(ReviewFlag)
class ReviewFlagAdmin(admin.ModelAdmin):
    list_display = ("review", "flagged_by", "reason", "created_at")
