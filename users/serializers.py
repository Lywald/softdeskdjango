from rest_framework.serializers import ModelSerializer

from users.models import  User

class UserSerializer(ModelSerializer):
    """Serialize/deserialize User instances for the API."""

    class Meta:
        """Serializer configuration for the User model."""
        model = User
        fields = [
            "id", "username", "password", "email", "first_name", "last_name",
            "age", "can_be_contacted", "can_data_be_shared",
        ]
        # Ensure password is accepted on write but never returned in responses.
        extra_kwargs = {"password": {"write_only": True}}