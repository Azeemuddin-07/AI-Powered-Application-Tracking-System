from django.db.models import Q
from django.utils import timezone
from rest_framework import filters, generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from apps.accounts.permissions import IsCandidate, IsRecruiter
from apps.jobs.models import Job
from .models import Application, ApplicationStatusHistory
from .serializers import ApplicationSerializer, StatusUpdateSerializer


class CandidateApplicationListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsCandidate]
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        return Application.objects.filter(candidate=self.request.user.candidate_profile).select_related("job__company", "resume").prefetch_related("status_history__changed_by")

    def perform_create(self, serializer):
        job = serializer.validated_data["job"]
        if job.status != Job.Status.PUBLISHED or (job.application_deadline and job.application_deadline < timezone.now()):
            raise ValidationError({"job": "This job is not accepting applications."})
        application = serializer.save(candidate=self.request.user.candidate_profile)
        ApplicationStatusHistory.objects.create(application=application, from_status="", to_status=Application.Status.APPLIED, changed_by=self.request.user)


class CandidateApplicationDetailView(generics.RetrieveAPIView):
    permission_classes = [IsCandidate]
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        return Application.objects.filter(candidate=self.request.user.candidate_profile).select_related("job__company", "resume").prefetch_related("status_history__changed_by")


class WithdrawApplicationView(generics.GenericAPIView):
    permission_classes = [IsCandidate]

    def post(self, request, pk):
        application = generics.get_object_or_404(Application, pk=pk, candidate=request.user.candidate_profile)
        if application.status in (Application.Status.HIRED, Application.Status.REJECTED, Application.Status.WITHDRAWN):
            raise ValidationError({"status": "This application can no longer be withdrawn."})
        previous = application.status
        application.status, application.withdrawn_at = Application.Status.WITHDRAWN, timezone.now()
        application.save(update_fields=["status", "withdrawn_at", "updated_at"])
        ApplicationStatusHistory.objects.create(application=application, from_status=previous, to_status=application.status, changed_by=request.user)
        return Response(ApplicationSerializer(application, context={"request": request}).data)


class RecruiterApplicationListView(generics.ListAPIView):
    permission_classes = [IsRecruiter]
    serializer_class = ApplicationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["candidate__user__first_name", "candidate__user__last_name", "candidate__user__email", "job__title"]
    ordering_fields = ["created_at", "status"]

    def get_queryset(self):
        qs = Application.objects.filter(job__company__recruiters=self.request.user.recruiter_profile).select_related("job__company", "candidate__user", "resume").prefetch_related("status_history__changed_by")
        if job := self.request.query_params.get("job"):
            qs = qs.filter(job_id=job)
        if state := self.request.query_params.get("status"):
            qs = qs.filter(status=state)
        return qs.order_by("-created_at")


class RecruiterApplicationDetailView(generics.RetrieveAPIView):
    permission_classes = [IsRecruiter]
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        return Application.objects.filter(job__company__recruiters=self.request.user.recruiter_profile).select_related("job__company", "candidate__user", "resume").prefetch_related("status_history__changed_by")


class ApplicationStatusUpdateView(generics.GenericAPIView):
    permission_classes = [IsRecruiter]
    serializer_class = StatusUpdateSerializer

    def patch(self, request, pk):
        application = generics.get_object_or_404(Application, pk=pk, job__company__recruiters=request.user.recruiter_profile)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        next_status = serializer.validated_data["status"]
        if application.status in (Application.Status.HIRED, Application.Status.WITHDRAWN) and next_status != application.status:
            raise ValidationError({"status": "This application is in a terminal state."})
        prior = application.status
        application.status = next_status
        application.save(update_fields=["status", "updated_at"])
        ApplicationStatusHistory.objects.create(application=application, from_status=prior, to_status=next_status, changed_by=request.user, reason=serializer.validated_data.get("reason", ""))
        application.refresh_from_db()
        return Response(ApplicationSerializer(application, context={"request": request}).data)
