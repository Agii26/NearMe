from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from businesses.models import Business


class Review(models.Model):
    """
    A consumer's rating + optional text review of a business. Visible
    immediately on submission (real review platforms lose their value if
    reviews sit in a pre-approval queue) — moderation is reactive via
    ReviewFlag below, not a pre-publish gate.
    """

    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    text = models.TextField(blank=True)
    is_removed = models.BooleanField(
        default=False,
        help_text="Set by an admin after reviewing a flag. Hides the review from all public views.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["business", "user"], name="one_review_per_user_per_business"
            )
        ]

    def __str__(self):
        return f"{self.user} rated {self.business} {self.rating}/5"


class ReviewFlag(models.Model):
    """
    A single flag doesn't hide a review by itself — that would make it
    trivial to suppress reviews you simply dislike. It surfaces the review
    in the admin's moderation queue for a human decision.
    """

    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="flags")
    flagged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["review", "flagged_by"], name="one_flag_per_user_per_review"
            )
        ]

    def __str__(self):
        return f"Flag on review #{self.review_id} by {self.flagged_by}"
