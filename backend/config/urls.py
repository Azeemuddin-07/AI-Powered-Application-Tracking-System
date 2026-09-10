from django.contrib import admin
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views import LoginView, MeView, RegisterView
from apps.applications.views import (ApplicationStatusUpdateView, CandidateApplicationDetailView, CandidateApplicationListCreateView, RecruiterApplicationDetailView, RecruiterApplicationListView, WithdrawApplicationView)
from apps.candidates.views import (CandidateProfileView, CandidateSkillDetail, CandidateSkillList, EducationDetail, EducationList, ExperienceDetail, ExperienceList, ResumeDetailView, ResumeDownloadView, ResumeListCreateView, SavedJobList, SavedJobToggleView)
from apps.dashboard_views import CandidateDashboardView, RecruiterDashboardView
from apps.jobs.views import JobDetailView, JobListCreateView, SkillListView
from apps.recruiters.views import CompanyDetailView, CompanyListCreateView, RecruiterProfileView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/register/", RegisterView.as_view()),
    path("api/v1/auth/login/", LoginView.as_view()),
    path("api/v1/auth/refresh/", TokenRefreshView.as_view()),
    path("api/v1/auth/me/", MeView.as_view()),
    path("api/v1/candidate/profile/", CandidateProfileView.as_view()),
    path("api/v1/candidate/dashboard/", CandidateDashboardView.as_view()),
    path("api/v1/candidate/skills/", CandidateSkillList.as_view()),
    path("api/v1/candidate/skills/<int:pk>/", CandidateSkillDetail.as_view()),
    path("api/v1/candidate/education/", EducationList.as_view()), path("api/v1/candidate/education/<int:pk>/", EducationDetail.as_view()),
    path("api/v1/candidate/experience/", ExperienceList.as_view()), path("api/v1/candidate/experience/<int:pk>/", ExperienceDetail.as_view()),
    path("api/v1/resumes/", ResumeListCreateView.as_view()), path("api/v1/resumes/<int:pk>/", ResumeDetailView.as_view()), path("api/v1/resumes/<int:pk>/download/", ResumeDownloadView.as_view()),
    path("api/v1/candidate/saved-jobs/", SavedJobList.as_view()), path("api/v1/jobs/<int:job_id>/save/", SavedJobToggleView.as_view()),
    path("api/v1/recruiter/profile/", RecruiterProfileView.as_view()), path("api/v1/recruiter/dashboard/", RecruiterDashboardView.as_view()),
    path("api/v1/companies/", CompanyListCreateView.as_view()), path("api/v1/companies/<int:pk>/", CompanyDetailView.as_view()),
    path("api/v1/skills/", SkillListView.as_view()), path("api/v1/jobs/", JobListCreateView.as_view()), path("api/v1/jobs/<int:pk>/", JobDetailView.as_view()),
    path("api/v1/applications/", CandidateApplicationListCreateView.as_view()), path("api/v1/applications/<int:pk>/", CandidateApplicationDetailView.as_view()), path("api/v1/applications/<int:pk>/withdraw/", WithdrawApplicationView.as_view()),
    path("api/v1/recruiter/applications/", RecruiterApplicationListView.as_view()), path("api/v1/recruiter/applications/<int:pk>/", RecruiterApplicationDetailView.as_view()), path("api/v1/recruiter/applications/<int:pk>/status/", ApplicationStatusUpdateView.as_view()),
    path("api/schema/", SpectacularAPIView.as_view()), path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="schema"),
]
