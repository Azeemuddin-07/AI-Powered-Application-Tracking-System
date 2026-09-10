import hashlib

from django.http import FileResponse

from django.conf import settings
from rest_framework import generics, parsers, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.accounts.permissions import IsCandidate
from .models import CandidateSkill, Education, Experience, Resume, SavedJob
from .serializers import CandidateProfileSerializer, CandidateSkillSerializer, EducationSerializer, ExperienceSerializer, ResumeSerializer, SavedJobSerializer


class CandidateProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsCandidate]
    serializer_class = CandidateProfileSerializer

    def get_object(self):
        return self.request.user.candidate_profile

    def perform_update(self, serializer):
        profile = serializer.save()
        completed = sum(bool(getattr(profile, field)) for field in ("phone", "location", "professional_summary", "linkedin_url", "github_url", "portfolio_url"))
        related = int(profile.resumes.exists()) + int(profile.candidate_skills.exists()) + int(profile.education.exists()) + int(profile.experience.exists())
        profile.profile_completion = min(100, round((completed + related) / 10 * 100))
        profile.save(update_fields=["profile_completion", "updated_at"])


class CandidateOwnedListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsCandidate]
    model = None

    def get_queryset(self):
        return self.model.objects.filter(candidate=self.request.user.candidate_profile)

    def perform_create(self, serializer):
        serializer.save(candidate=self.request.user.candidate_profile)


class CandidateOwnedDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsCandidate]
    model = None

    def get_queryset(self):
        return self.model.objects.filter(candidate=self.request.user.candidate_profile)


class CandidateSkillList(CandidateOwnedListCreateView):
    model, serializer_class = CandidateSkill, CandidateSkillSerializer


class CandidateSkillDetail(CandidateOwnedDetailView):
    model, serializer_class = CandidateSkill, CandidateSkillSerializer


class EducationList(CandidateOwnedListCreateView):
    model, serializer_class = Education, EducationSerializer


class EducationDetail(CandidateOwnedDetailView):
    model, serializer_class = Education, EducationSerializer


class ExperienceList(CandidateOwnedListCreateView):
    model, serializer_class = Experience, ExperienceSerializer


class ExperienceDetail(CandidateOwnedDetailView):
    model, serializer_class = Experience, ExperienceSerializer


class ResumeListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsCandidate]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    serializer_class = ResumeSerializer

    def get_queryset(self):
        return Resume.objects.filter(candidate=self.request.user.candidate_profile).order_by("-created_at")

    def perform_create(self, serializer):
        upload = self.request.FILES.get("file")
        max_size = int(getattr(settings, "MAX_RESUME_UPLOAD_BYTES", 10 * 1024 * 1024))
        if not upload or upload.content_type != "application/pdf" or not upload.name.lower().endswith(".pdf"):
            raise ValidationError({"file": "Upload a PDF resume."})
        if upload.size > max_size:
            raise ValidationError({"file": f"Resume must be smaller than {max_size // 1024 // 1024} MB."})
        digest = hashlib.sha256(upload.read()).hexdigest()
        upload.seek(0)
        if Resume.objects.filter(candidate=self.request.user.candidate_profile, content_hash=digest).exists():
            raise ValidationError({"file": "This resume has already been uploaded."})
        Resume.objects.filter(candidate=self.request.user.candidate_profile, is_primary=True).update(is_primary=False)
        serializer.save(candidate=self.request.user.candidate_profile, original_filename=upload.name, file_size=upload.size, content_hash=digest, is_primary=True)


class ResumeDetailView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsCandidate]
    serializer_class = ResumeSerializer

    def get_queryset(self):
        return Resume.objects.filter(candidate=self.request.user.candidate_profile)


class ResumeDownloadView(generics.GenericAPIView):
    """Serve a resume only to its owner or a recruiter with an application for it."""

    def get(self, request, pk):
        resume = generics.get_object_or_404(Resume, pk=pk)
        is_owner = request.user.role == "candidate" and resume.candidate.user_id == request.user.id
        is_authorized_recruiter = request.user.role == "recruiter" and resume.applications.filter(job__company__recruiters=request.user.recruiter_profile).exists()
        if not (is_owner or is_authorized_recruiter):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not have access to this resume.")
        return FileResponse(resume.file.open("rb"), as_attachment=False, filename=resume.original_filename)


class SavedJobList(generics.ListAPIView):
    permission_classes = [IsCandidate]
    serializer_class = SavedJobSerializer

    def get_queryset(self):
        return SavedJob.objects.filter(candidate=self.request.user.candidate_profile).select_related("job__company")


class SavedJobToggleView(generics.GenericAPIView):
    permission_classes = [IsCandidate]

    def post(self, request, job_id):
        from apps.jobs.models import Job
        job = generics.get_object_or_404(Job, pk=job_id, status=Job.Status.PUBLISHED)
        saved, created = SavedJob.objects.get_or_create(candidate=request.user.candidate_profile, job=job)
        if not created:
            saved.delete()
        return Response({"saved": created}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    permission_classes = [permissions.IsAuthenticated]
