from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from users.models import User
from users.serializers import UserSerializer

class UserAPIView(APIView):
    """Read-only endpoint to list users.

    Methods
    -------
    GET
        Returns an array of serialized users using ``UserSerializer`` (many=True).

    Response
    --------
    200 OK
        JSON list of user objects with fields defined in ``UserSerializer``.
    """

    def get(self, *args, **kwargs):
        """List all users as serialized JSON."""
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
# Create your views here.

class UserViewset(ModelViewSet):
    """CRUD API for users using DRF's ModelViewSet."""

    serializer_class = UserSerializer

    def get_queryset(self):
        """Return the base queryset of all users."""
        return User.objects.all()