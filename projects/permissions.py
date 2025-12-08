"""
┌─────────────────────┬──────────────┬─────────────────┬──────────────────┐
│ Ressource           │ Non-Auth     │ Contributeur    │ Auteur           │
├─────────────────────┼──────────────┼─────────────────┼──────────────────┤
│ Project LIST        │ ❌ 401       │ ✅ GET          │ ✅ GET           │
│ Project CREATE      │ ❌ 401       │ ✅ POST         │ ✅ POST          │
│ Project READ        │ ❌ 401       │ ✅ GET          │ ✅ GET           │
│ Project UPDATE      │ ❌ 401       │ ❌ 403          │ ✅ PUT           │
│ Project DELETE      │ ❌ 401       │ ❌ 403          │ ✅ DELETE        │
├─────────────────────┼──────────────┼─────────────────┼──────────────────┤
│ Issue in Project    │ ❌ 401       │ ✅ GET/POST     │ ✅ ALL           │
│ Issue by Other      │ ❌ 401       │ ✅ GET (l.seule)│ ✅ All           │
│ Comment in Issue    │ ❌ 401       │ ✅ GET/POST     │ ✅ ALL           │
│ Comment by Author   │ ❌ 401       │ ❌ 403 (PUT)    │ ✅ PUT/DELETE    │
└─────────────────────┴──────────────┴─────────────────┴──────────────────┘


## Matrice de Test Complète

| Test | HTTP | Endpoint | Token | Attendu |
|------|------|----------|-------|---------|
| Sans auth | GET | /api/projects/ | ❌ | 401 |
| Alice lit ses projets | GET | /api/projects/ | alice | 200 |
| Alice crée projet | POST | /api/projects/ | alice | 201 |
| Alice modifie son projet | PUT | /api/projects/1/ | alice | 200 |
| Bob lit le projet d'Alice | GET | /api/projects/1/ | bob | 200 |
| Bob modifie le projet d'Alice | PUT | /api/projects/1/ | bob | 403 |
| Bob crée issue (contributeur) | POST | /api/issues/ | bob | 201 |
| Bob modifie sa issue | PUT | /api/issues/1/ | bob | 200 |
| Alice modifie issue de Bob | PUT | /api/issues/1/ | alice | 403 |
| Non-contributeur lit issue | GET | /api/issues/1/ | charlie | 403 |

"""

from projects.models import Contributor, Issue, Project
from rest_framework import permissions


class ContributorPermission(permissions.BasePermission):
    """
    Permissions for managing project contributors.
    
    - Project author: Can POST (add) and DELETE contributors
    - Project members: Can GET (read) other contributors
    - Others: No access (403)
    """
    
    def has_permission(self, request, view):
        # Staff can do anything
        if request.user.is_staff:
            return True
        
        # Others can read (we added IsAuthenticated in the view)
        if request.method in permissions.SAFE_METHODS:
            return None
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user can access a specific contributor instance.
        
        Args:
            obj: Contributor instance
            
        Returns:
            True if user is project author (all methods) or project member (GET only)
            False otherwise
        """
        # Project author can do anything
        if request.user == obj.project.author:
            return True
        
        # Project members can read only
        is_proj_member = obj.project.contributors.filter(user=request.user).exists()
        
        if is_proj_member and request.method in permissions.SAFE_METHODS:
            return True
        
        return False
        
    
class ProjectPermission(permissions.BasePermission):
    """
    Permissions for managing projects.
    
    - Project author: Can GET, POST (create), PUT (update), and DELETE
    - Project contributors: Can GET (read) only
    - Others: Cannot access (filtered by get_queryset())
    """
    
    def has_permission(self, request, view):
        """
        Check if user can access the list/create endpoint.
        
        Staff can do anything. GET requests deferred to IsAuthenticated.
        POST requests allowed for authenticated users (detail check in has_object_permission).
        """
        # Staff can do anything
        if request.user.is_staff:
            return True
        
        # Others can read (we added IsAuthenticated permission in the view)
        if request.method in permissions.SAFE_METHODS:
            return None
        
        if request.method == "POST":
            return True

        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user can access a specific project instance.
        
        Args:
            obj: Project instance
            
        Returns:
            True if user is project author (all methods) or contributor (GET only)
            False for all other cases
        """
        # Project author can do anything
        if request.user == obj.author:
            return True
        
        # Contributors can only read
        if request.method == "PUT" or request.method == "DELETE":
            return False
        else:
            return True
            

class CommentPermission(permissions.BasePermission):
    """
    Permissions for managing comments on issues.
    
    - Comment author: Can GET, POST (create), PUT (update), and DELETE their comments
    - Project members (author/contributors): Can GET (read) only
    - Non-members: Cannot access
    """
    
    def has_permission(self, request, view):
        """
        Check if user can access the list/create endpoint.
        
        Staff can do anything. GET requests deferred to IsAuthenticated.
        POST requests allowed for authenticated users (detail check in has_object_permission).
        """
        # Staff can do anything
        if request.user.is_staff:
            return True
        
        # Others can read (we added IsAuthenticated in the view)
        if request.method in permissions.SAFE_METHODS:
            return None
        
        return True # Filtered further in has_object_permission
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user can access a specific comment instance.
        
        Args:
            obj: Comment instance
            
        Returns:
            True if user is comment author (all methods) or project member (GET only)
            False otherwise
        """
        # Comment author can do everything
        if request.user == obj.author:
            return True
        
        # Project members can read only
        is_author = obj.issue.project.author == request.user
        is_contributor = obj.issue.project.contributors.filter(user=request.user).exists()
        if is_author or is_contributor:
            return request.method in permissions.SAFE_METHODS
    
        return False
    

class IssuePermission(permissions.BasePermission):
    """
    Permissions for managing issues in projects.
    
    - Issue author: Can GET, POST (create), PUT (update), and DELETE their issues
    - Project members (author/contributors): Can GET (read) and POST (create) only
    - Non-members: Cannot access
    """
    
    def has_permission(self, request, view):
        """
        Check if user can access the list/create endpoint.
        
        Staff can do anything. GET requests deferred to IsAuthenticated.
        POST/PUT/DELETE requests allowed for authenticated users (detail check in has_object_permission).
        """
        # Staff can do anything
        if request.user.is_staff:
            return True
        
        # Others can read (we added IsAuthenticated in the view)
        if request.method in permissions.SAFE_METHODS:
            return None
        
        if request.method == "POST":
            # Allow Issue creation for every authenticated user
            return True

        # Allow Issue PUT/DELETE 
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user can access a specific issue instance.
        
        Args:
            obj: Issue instance
            
        Returns:
            True if user is issue author (all methods) or project member (GET/POST only)
            False otherwise
        """
        # Issue author can do everything
        if request.user == obj.author:
            return True
        
        is_contributor = obj.project.contributors.filter(user=request.user).exists()
        if is_contributor:
            return request.method in permissions.SAFE_METHODS
        
        return False
    