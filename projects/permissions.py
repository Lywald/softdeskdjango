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
    def has_permission(self, request, view):
        # Staff can do anything
        if request.user.is_staff:
            return True
        
        # We can read (we added IsAuthenticated in the view)
        if request.method in permissions.SAFE_METHODS:
            return None
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # per-item permission: 
        # -- project author can create/delete contributor
        # -- contributors can read their project's other contributors' profile
        # -- others can do nothing
        if request.user == obj.project.author:
            return True
        
        proj = None

        if hasattr(obj, 'project'):
            proj = obj.project
        elif hasattr(obj, 'issue'):
            proj = obj.issue.project
        else:
            return False

        is_proj_member = None

        if proj:
            is_proj_member = request.user == proj.author or proj.contributors.filter(user=request.user).exists()
        
        if is_proj_member and request.method in permissions.SAFE_METHODS:
            return True
        
        return False
        
    
class ProjectPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Staff can do anything
        if request.user.is_staff:
            return True
        
        # We can read (we added IsAuthenticated in the view)
        if request.method in permissions.SAFE_METHODS:
            return None
        
        if request.method == "POST":
            return True

        return False
    
    def has_object_permission(self, request, view, obj):
        # Project author can do anything, others can only read or create
        if request.user == obj.author:
            return True
        
        if request.method == "PUT" or request.method == "DELETE":
            return False
        else:
            return True
            

class CommentPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Staff can do anything
        if request.user.is_staff:
            return True
        
        # We can read (we added IsAuthenticated in the view)
        if request.method in permissions.SAFE_METHODS:
            return None
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # l'auteur du commentaire peut tout faire
        # les membres du projet peuvent lire les commentaires
        # les autres ne peuvent ni lire ni écrire
        if request.user == obj.author:
            return True
        
        is_author = obj.issue.project.author == request.user
        is_contributor = obj.issue.project.contributors.filter(user=request.user).exists()
        if is_author or is_contributor:
            return request.method in permissions.SAFE_METHODS
    
        return False
    

class IssuePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Staff can do anything
        if request.user.is_staff:
            return True
        
        # We can read (we added IsAuthenticated in the view)
        if request.method in permissions.SAFE_METHODS:
            return None
        
        if request.method == "POST":
            return True

        return False
    
    def has_object_permission(self, request, view, obj):
        if request.user == obj.author:
            return True
        
        is_contributor = obj.project.contributors.filter(user=request.user).exists()
        if is_contributor:
            return request.method in permissions.SAFE_METHODS
        
        return False


""" 
class AuthorOrAdminCanCRUD(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if (request.user == obj.author) or (request.user.is_staff):
            return True
        return False


class IssueOrCommentContributersOrCanRead(AuthorOrAdminCanCRUD):
    def has_object_permission(self, request, view, obj):
        isAuthorOrStaff = super().has_object_permission(request, view, obj)
        if isAuthorOrStaff == True:
            return True
        
        if hasattr(obj, 'project'):
            proj = obj.project
        elif hasattr(obj, 'issue'):
            proj = obj.issue.project
        else:
            return False
        
        # check if contributor
        is_project_member = request.user == proj.author or proj.contributors.filter(user=request.user).exists()

        if is_project_member == True:
            return True
        
        return False

class ContributorOrStaffPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.user == obj.user) or (request.user.is_staff) """