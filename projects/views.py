from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Project, Contributor, Issue, Comment
from .serializers import ProjectSerializer, ContributorSerializer, IssueSerializer, CommentSerializer
from users.models import User


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    # permission_classes = [IsAuthenticated]  # Commented out for testing

    def perform_create(self, serializer):
        # For testing, use the first user if no authentication
        author = self.request.user if self.request.user.is_authenticated else User.objects.first()
        serializer.save(author=author)


class ContributorViewSet(viewsets.ModelViewSet):
    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    # permission_classes = [IsAuthenticated]  # Commented out for testing


class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    # permission_classes = [IsAuthenticated]  # Commented out for testing

    def perform_create(self, serializer):
        # For testing, use the first user if no authentication
        author = self.request.user if self.request.user.is_authenticated else User.objects.first()
        serializer.save(author=author)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    # permission_classes = [IsAuthenticated]  # Commented out for testing

    def perform_create(self, serializer):
        # For testing, use the first user if no authentication
        author = self.request.user if self.request.user.is_authenticated else User.objects.first()
        serializer.save(author=author)
