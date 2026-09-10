from django.db.models import Count
from django.utils import timezone
from rest_framework import filters, generics, permissions
from rest_framework.exceptions import PermissionDenied

from apps.accounts.permissions import IsRecruiter
from .models import Job, Skill
from .serializers import JobDetailSerializer, JobListSerializer, JobWriteSerializer, SkillSerializer


class SkillListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SkillSerializer
    queryset = Skill.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "category"]


class JobListCreateView(generics.ListCreateAPIView):
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "company__name", "location", "job_skills__skill__name"]
    ordering_fields = ["created_at", "published_at", "salary_min"]

    def get_permissions(self):
        return [IsRecruiter()] if self.request.method == "POST" else [permissions.AllowAny()]

    def get_queryset(self):
        qs = Job.objects.select_related("company").annotate(applications_count=Count("applications"))
        if self.request.user.is_authenticated and self.request.user.role == "recruiter" and self.request.query_params.get("mine") == "true":
            qs = qs.filter(company__recruiters=self.request.user.recruiter_profile)
        else:
            qs = qs.filter(status=Job.Status.PUBLISHED, published_at__lte=timezone.now())
        params = self.request.query_params
        for key in ("location", "employment_type", "experience_level", "workplace_type"):
            if value := params.get(key):
                qs = qs.filter(**{f"{key}__iexact": value})
        if skill := params.get("skill"):
            qs = qs.filter(job_skills__skill__slug=skill)
        if salary := params.get("salary_min"):
            qs = qs.filter(salary_max__gte=salary)
        return qs.distinct().order_by("-published_at", "-created_at")

    def get_serializer_class(self):
        return JobWriteSerializer if self.request.method == "POST" else JobListSerializer

    def perform_create(self, serializer):
        if not serializer.validated_data["company"].recruiters.filter(pk=self.request.user.recruiter_profile.pk).exists():
            raise PermissionDenied("You can only post jobs for your companies.")
        serializer.save()


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    def get_permissions(self):
        return [IsRecruiter()] if self.request.method in ("PATCH", "PUT", "DELETE") else [permissions.AllowAny()]

    def get_queryset(self):
        qs = Job.objects.select_related("company").prefetch_related("job_skills__skill").annotate(applications_count=Count("applications"))
        if self.request.method in ("PATCH", "PUT", "DELETE"):
            return qs.filter(company__recruiters=self.request.user.recruiter_profile)
        return qs.filter(status=Job.Status.PUBLISHED, published_at__lte=timezone.now())

    def get_serializer_class(self):
        return JobWriteSerializer if self.request.method in ("PATCH", "PUT") else JobDetailSerializer

    def perform_update(self, serializer):
        serializer.save()
