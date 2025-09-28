from django.contrib import admin
from .models import Project, Contributor, Issue, Comment


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'author', 'created_time')
    list_filter = ('type', 'created_time')
    search_fields = ('name', 'description')


@admin.register(Contributor)
class ContributorAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'created_time')
    list_filter = ('created_time',)
    search_fields = ('user__username', 'project__name')


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'priority', 'tag', 'status', 'author', 'assignee', 'created_time')
    list_filter = ('priority', 'tag', 'status', 'created_time')
    search_fields = ('name', 'description', 'project__name')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'issue', 'author', 'created_time')
    list_filter = ('created_time',)
    search_fields = ('description', 'issue__name')
