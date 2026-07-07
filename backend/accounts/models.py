from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    CONSUMER = "consumer"
    BUSINESS_OWNER = "business_owner"
    ROLE_CHOICES = [
        (CONSUMER, "Consumer"),
        (BUSINESS_OWNER, "Business owner"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CONSUMER)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    """Every user gets a Profile the moment they're created — nothing in the
    app should ever have to handle a User with no Profile."""
    if created:
        Profile.objects.get_or_create(user=instance)
