
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    message = "Only admin can access this resource."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "admin"
        )


class IsEmployer(BasePermission):
    message = "Only employers can access this resource."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "employer"
        )


class IsCandidate(BasePermission):
    message = "Only candidates can access this resource."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "candidate"
        )
