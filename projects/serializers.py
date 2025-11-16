from rest_framework import serializers
from .models import Project, Contributor, Issue, Comment


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project model.
    - Only exposes public fields
    - author is read-only and auto-set during creation
    """

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'type', 'author', 'created_time']
        read_only_fields = ['id', 'author', 'created_time']


class ContributorSerializer(serializers.ModelSerializer):
    """
    Serializer for Contributor model.
    - Links users to projects
    - Only project author can manage contributors
    """

    class Meta:
        model = Contributor
        fields = ['id', 'user', 'project', 'created_time']
        read_only_fields = ['id', 'created_time']


class IssueSerializer(serializers.ModelSerializer):
    """
    Serializer for Issue model.
    - Issues belong to projects
    - author and assignee are handled separately for security
    """

    class Meta:
        model = Issue
        fields = ['id', 'name', 'description', 'priority', 'tag', 'status', 'project', 'author', 'assignee', 'created_time']
        read_only_fields = ['id', 'author', 'created_time']


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.
    - Comments are linked to issues
    - author is auto-set during creation
    """

    class Meta:
        model = Comment
        fields = ['id', 'description', 'issue', 'author', 'created_time']
        read_only_fields = ['id', 'author', 'created_time']