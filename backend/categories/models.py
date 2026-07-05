from django.db import models


class Category(models.Model):
    """Business taxonomy — seeded once, referenced by every Business."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Icon identifier used by the frontend, e.g. a Tabler icon name.",
    )

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name
