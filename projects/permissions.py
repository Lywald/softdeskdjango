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
        

class IsIssueAuthorOrProjectContributorReadOnly(UserIsAuthenticated):
    """
    Permission for Issues:
    - Visible to project author and all contributors (READ)
    - Modifiable/Deletable only by issue author (WRITE)
    
    Spec: "Un problème ne peut être actualisé ou supprimé que par son auteur,
    mais il doit rester visible par tous les contributeurs au projet."
    """
        
    def has_object_permission(self, request, view, obj):
        """
        Check issue access permissions:
        - Must be project member (author or contributor) to view
        - Only issue author can modify/delete
        """
        proj = obj.project
        user = request.user
        
        # Staff bypass all permissions
        staff_check = super().has_object_permission(request, view, obj)
        if staff_check is True:
            return True
        
        if user == proj.author or proj.contributors.filter(user=user).exists():
            return True        

        # Write: only issue author
        return obj.author == user        
    

class IsCommentAuthorOrProjectContributorReadOnly(UserIsAuthenticated):
    """
    Permission for Comments:
    - Visible to project author and all contributors (READ)
    - Modifiable/Deletable only by comment author (WRITE)
    
    Spec: "Les commentaires doivent être visibles par tous les contributeurs au projet
    et par le responsable du projet, mais seul leur auteur peut les actualiser ou les supprimer."
    """

    def has_object_permission(self, request, view, obj):
        """
        Check comment access permissions:
        - Must be project member (author or contributor) to view
        - Only comment author can modify/delete
        """
        user = request.user
        project = obj.issue.project

        # Staff bypass all permissions
        staff_check = super.has_object_permission(request, view, obj)
        if staff_check is True:
            return True

        if user == project.author or project.contributors.filter(user=user).exists():
            return True
        
        return False
