from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from apps.applications.models import Application
from apps.jobs.models import Job


class HiringWorkflowTests(TestCase):
    def register_and_login(self, role, email):
        client = APIClient()
        register = client.post("/api/v1/auth/register/", {"name": role.title(), "email": email, "password": "A-strong-password-123", "confirm_password": "A-strong-password-123", "role": role}, format="json")
        self.assertEqual(register.status_code, 201, register.data)
        login = client.post("/api/v1/auth/login/", {"username": email, "password": "A-strong-password-123"}, format="json")
        self.assertEqual(login.status_code, 200, login.data)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        return client

    def test_candidate_can_apply_and_recruiter_can_update_status(self):
        recruiter = self.register_and_login("recruiter", "recruiter@example.com")
        company = recruiter.post("/api/v1/companies/", {"name": "Acme", "slug": "acme"}, format="json")
        self.assertEqual(company.status_code, 201, company.data)
        job = recruiter.post("/api/v1/jobs/", {"company": company.data["id"], "title": "Backend Engineer", "description": "Build APIs.", "experience_level": "Mid", "employment_type": "Full-time", "workplace_type": "remote", "location": "Remote", "status": "published"}, format="json")
        self.assertEqual(job.status_code, 201, job.data)
        candidate = self.register_and_login("candidate", "candidate@example.com")
        resume = candidate.post("/api/v1/resumes/", {"file": SimpleUploadedFile("resume.pdf", b"%PDF-1.4 test", content_type="application/pdf")}, format="multipart")
        self.assertEqual(resume.status_code, 201, resume.data)
        application = candidate.post("/api/v1/applications/", {"job": job.data["id"], "resume": resume.data["id"], "cover_letter": "I am interested."}, format="json")
        self.assertEqual(application.status_code, 201, application.data)
        recruiter_apps = recruiter.get("/api/v1/recruiter/applications/")
        self.assertEqual(recruiter_apps.data["count"], 1)
        updated = recruiter.patch(f"/api/v1/recruiter/applications/{application.data['id']}/status/", {"status": "shortlisted"}, format="json")
        self.assertEqual(updated.status_code, 200, updated.data)
        self.assertEqual(Application.objects.get().status, Application.Status.SHORTLISTED)

    def test_candidate_cannot_create_job_or_see_recruiter_applicants(self):
        candidate = self.register_and_login("candidate", "candidate@example.com")
        self.assertEqual(candidate.post("/api/v1/jobs/", {}, format="json").status_code, 403)
        self.assertEqual(candidate.get("/api/v1/recruiter/applications/").status_code, 403)
