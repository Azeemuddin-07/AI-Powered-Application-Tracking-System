from django.db.models import Count
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsCandidate, IsRecruiter
from apps.applications.models import Application
from apps.jobs.models import Job


class CandidateDashboardView(APIView):
    permission_classes = [IsCandidate]

    def get(self, request):
        applications = Application.objects.filter(candidate=request.user.candidate_profile).select_related("job__company")
        recent = applications.order_by("-created_at")[:5]
        from apps.applications.serializers import ApplicationSerializer
        from apps.jobs.serializers import JobListSerializer
        recommended = Job.objects.filter(status=Job.Status.PUBLISHED).select_related("company").order_by("-published_at")[:4]
        return Response({"profile_completion": request.user.candidate_profile.profile_completion, "total_applications": applications.count(), "under_review": applications.filter(status=Application.Status.UNDER_REVIEW).count(), "shortlisted": applications.filter(status=Application.Status.SHORTLISTED).count(), "recent_applications": ApplicationSerializer(recent, many=True, context={"request": request}).data, "recent_jobs": JobListSerializer(recommended, many=True).data})


class RecruiterDashboardView(APIView):
    permission_classes = [IsRecruiter]

    def get(self, request):
        jobs = Job.objects.filter(company__recruiters=request.user.recruiter_profile)
        applications = Application.objects.filter(job__in=jobs)
        return Response({"total_jobs": jobs.count(), "active_jobs": jobs.filter(status=Job.Status.PUBLISHED).count(), "total_applicants": applications.count(), "shortlisted": applications.filter(status=Application.Status.SHORTLISTED).count(), "hires": applications.filter(status=Application.Status.HIRED).count(), "recent_applications": list(applications.order_by("-created_at").values("id", "status", "created_at", "job__title", "candidate__user__first_name", "candidate__user__last_name")[:5])})
