from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from .models import Business, BusinessClaim, Media


@admin.register(Business)
class BusinessAdmin(GISModelAdmin):
    list_display = ("name", "category", "claimed", "osm_id", "updated_at")
    list_filter = ("category", "claimed")
    search_fields = ("name", "address", "osm_id")


@admin.action(description="Approve selected claims")
def approve_claims(modeladmin, request, queryset):
    for claim in queryset.filter(status=BusinessClaim.PENDING):
        claim.approve()


@admin.action(description="Reject selected claims")
def reject_claims(modeladmin, request, queryset):
    for claim in queryset.filter(status=BusinessClaim.PENDING):
        claim.reject()


@admin.register(BusinessClaim)
class BusinessClaimAdmin(admin.ModelAdmin):
    list_display = ("business", "user", "status", "created_at", "reviewed_at")
    list_filter = ("status",)
    actions = [approve_claims, reject_claims]


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ("business", "uploaded_by", "created_at")
