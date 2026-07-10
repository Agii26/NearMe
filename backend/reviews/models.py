from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from businesses.models import Business


class Review(models.Model):
    """
    A consumer's rating + optional text review of a business. Visible
    immediately on submission (real review platforms lose their value if
    reviews sit in a pre-approval queue) — but per the roadmap spec, a flag
    *does* pull it from public view pending a moderation decision (see
    ReviewFlag.save() below), not just a reactive queue that never hides
    anything. The known trade-off — a single flag can temporarily hide a
    review someone just disliked — is accepted as-specified rather than
    silently overridden; worth a real discussion if it becomes a problem
    in practice, not a unilateral code-level decision.
    """

    VISIBLE = "visible"
    HIDDEN_PENDING_REVIEW = "hidden_pending_review"
    REMOVED = "removed"
    STATUS_CHOICES = [
        (VISIBLE, "Visible"),
        (HIDDEN_PENDING_REVIEW, "Hidden — pending moderation"),
        (REMOVED, "Removed"),
    ]

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
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default=VISIBLE)
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

    def restore(self):
        self.status = self.VISIBLE
        self.save()

    def remove(self):
        self.status = self.REMOVED
        self.save()


class ReviewFlag(models.Model):
    """Reporting a review pulls it from public view immediately, pending
    a moderation decision — see Review.STATUS_CHOICES."""

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

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new and self.review.status == Review.VISIBLE:
            self.review.status = Review.HIDDEN_PENDING_REVIEW
            self.review.save()
