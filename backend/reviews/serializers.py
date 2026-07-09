from rest_framework import serializers

from .models import Review, ReviewFlag


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "business",
            "username",
            "rating",
            "text",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["business", "created_at", "updated_at"]


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["rating", "text"]

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class ReviewFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewFlag
        fields = ["id", "reason", "created_at"]
        read_only_fields = ["created_at"]
