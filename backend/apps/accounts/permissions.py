from rest_framework.permissions import BasePermission


class HasRole(BasePermission):
    roles: tuple[str, ...] = ()

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in self.roles and not request.user.is_suspended)


class IsCandidate(HasRole):
    roles = ("candidate",)


class IsRecruiter(HasRole):
    roles = ("recruiter",)
