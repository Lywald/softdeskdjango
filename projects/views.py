from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Project, Contributor, Issue, Comment
from .serializers import ProjectSerializer, ContributorSerializer, IssueSerializer, CommentSerializer
from .permissions import CommentPermission, ContributorPermission, IssuePermission, ProjectPermission
from users.models import User


class ProjectViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Projects.
    - Authors can create, read, update, delete their own projects
    - Other authenticated users can only read projects
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, ProjectPermission] #AuthorOrAdminCanCRUD]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        user = self.request.user
        
        if user.is_staff:
            return Project.objects.all()
        
        authored = Project.objects.filter(author=user)
        contributed = Project.objects.filter(contributors__user=user)
        user_projects = (authored | contributed).distinct()

        return user_projects

class ContributorViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Contributors.
    - Project author can add/remove contributors
    - Authenticated users can view contributors
    """

    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated, ContributorPermission] #ContributorOrStaffPermission]

    def get_queryset(self):
        """Filter contributors by project if project_id is provided."""
        queryset = Contributor.objects.all()
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset


class IssueViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Issues.
    - Issue author can update/delete their own issues
    - Project author and contributors can read issues
    - Only project members can create/read issues in a project
    """

    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, IssuePermission] #IssueOrCommentContributersOrCanRead]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        user = self.request.user
        
        if user.is_staff:
            return Issue.objects.all()
        
        authored = Project.objects.filter(author=user)
        contributed = Project.objects.filter(contributors__user=user)
        user_issues = (authored | contributed).distinct()

        return Issue.objects.filter(project__in=user_issues)


class CommentViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Comments.
    - Comment author can update/delete their own comments
    - Only project members can view/create comments on issues
    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, CommentPermission] #IssueOrCommentContributersOrCanRead]

    def get_queryset(self):
        """
        Filter comments to only show those from projects where user is a member.
        """
        user = self.request.user

        if user.is_staff:
            return Comment.objects.all()
        
        authored = Project.objects.filter(author=user)
        contributed = Project.objects.filter(contributors__user=user)
        user_projects = (authored | contributed).distinct()

        return Comment.objects.filter(issue__project__in=user_projects)
        


    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
