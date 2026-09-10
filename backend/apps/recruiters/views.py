from rest_framework import generics

from apps.accounts.permissions import IsRecruiter
from .models import Company
from .serializers import CompanySerializer, RecruiterProfileSerializer


class RecruiterProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsRecruiter]
    serializer_class = RecruiterProfileSerializer

    def get_object(self):
        return self.request.user.recruiter_profile


class CompanyListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsRecruiter]
    serializer_class = CompanySerializer

    def get_queryset(self):
        return Company.objects.filter(recruiters=self.request.user.recruiter_profile)

    def perform_create(self, serializer):
        company = serializer.save()
        company.recruiters.add(self.request.user.recruiter_profile)


class CompanyDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsRecruiter]
    serializer_class = CompanySerializer

    def get_queryset(self):
        return Company.objects.filter(recruiters=self.request.user.recruiter_profile)
