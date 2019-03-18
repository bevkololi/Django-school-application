from rest_framework import permissions


class IsSchoolOwnerOrReadOnly(permissions.BasePermission):
    message = "You are nor allowed to modify these details"

    def has_object_permission(self, request, view, obj):
        return obj.school == request.user


class IsNotSchoolOwner(permissions.BasePermission):
    message = "You action is restricted to other users"

    def has_object_permission(self, request, view, obj):
        return obj.shule != request.user
