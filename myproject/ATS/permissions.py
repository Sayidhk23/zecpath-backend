from rest_framework.permissions import BasePermission


class IsJobOwnerOrAdmin(BasePermission):
    
    message = "Only the job owner or an admin can access this resource."

    def has_object_permission(self, request, view, obj):

        if not request.user.is_authenticated:
            return False

        if request.user.role == "admin":
            return True

        if request.user.role == "employer":
            return obj.employer.user_id == request.user.id

        return False