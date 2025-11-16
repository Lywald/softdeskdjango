"""
Custom permission classes for SoftDesk API.

Implements role-based access control:
- IsAuthor: Only the author can modify their resource
- IsAuthorOrReadOnly: Author can modify, others can only read
- IsProjectAuthorOrContributor: Project author + contributors can access project resources
"""

from rest_framework import permissions


class UserIsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        # User must be authenticated
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # If user is staff, allow all 
        if request.user.is_staff:
            return True
        
        return None
    

class IsAuthorOrReadOnly(UserIsAuthenticated):
    """
    Permission to ensure only the author of a resource can modify it.
    Others can read the resource.
    Used for: Projects, Issues
    """

    def has_object_permission(self, request, view, obj):
        """Allow read for all, write only for the project author."""
        staff_check = super().has_object_permission(request, view, obj)
        if staff_check is True:
            return True
        
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the author
        return obj.author == request.user


class IsProjectAuthor(UserIsAuthenticated):
    """
    Permission for Contributors management:
    - Only project author can add/remove contributors
    
    Used for: ContributorViewSet
    """

    def has_object_permission(self, request, view, obj):
        """Only project author can manage contributors."""
        staff_check = super().has_object_permission(request, view, obj)
        if staff_check is True:
            return True

        # Write: only project author
        return obj.project.author == request.user
        

class IsAuthorOrProjectContributorReadOnly(UserIsAuthenticated):
    """
    Permission for Issues and Comments:
    - Visible to project author and all contributors (READ)
    - Modifiable/Deletable only by object author (WRITE)
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Staff bypass all permissions
        staff_check = super().has_object_permission(request, view, obj)
        if staff_check is True:
            return True

        # Determine the project (works for both Issue and Comment)
        if hasattr(obj, 'project'):
            project = obj.project
        elif hasattr(obj, 'issue'):
            project = obj.issue.project
        else:
            return False

        # User must be project member (author or contributor)
        is_project_member = user == project.author or project.contributors.filter(user=user).exists()
        if not is_project_member:
            return False

        # Read: all project members
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write: only object author
        return obj.author == user