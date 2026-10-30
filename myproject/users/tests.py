
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from ATS.models import Job
from .models import Employer


class AuthenticationTests(APITestCase):

    def test_profile_requires_authentication(self):
        """Unauthenticated users should not access the profile."""
        response = self.client.get(
            reverse("profile")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_invalid_login_is_rejected(self):
        """Invalid credentials should not return a successful login."""
        response = self.client.post(
            reverse("login"),
            {
                "username": "invalid_user",
                "password": "WrongPassword123!"
            },
            format="json"
        )

        self.assertNotEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_invalid_refresh_token_is_rejected(self):
        """An invalid refresh token should be rejected."""
        response = self.client.post(
            reverse("token_refresh"),
            {
                "refresh": "invalid.refresh.token"
            },
            format="json"
        )

        self.assertNotEqual(
            response.status_code,
            status.HTTP_200_OK
        )


    
    def test_candidate_registration_success(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "test_candidate_15",
                "email": "candidate15@example.com",
                "phone": "9876543210",
                "password": "StrongPass123!",
                "role": "candidate",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_duplicate_email_is_rejected(self):
        payload = {
            "username": "candidate_first",
            "email": "duplicate15@example.com",
            "phone": "9876543210",
            "password": "StrongPass123!",
            "role": "candidate",
        }

        first_response = self.client.post(
            reverse("register"), payload, format="json"
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        payload["username"] = "candidate_second"
        payload["email"] = "DUPLICATE15@example.com"

        second_response = self.client.post(
            reverse("register"), payload, format="json"
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_short_password_is_rejected(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "short_password_user",
                "email": "shortpass15@example.com",
                "phone": "9876543210",
                "password": "abc123",
                "role": "candidate",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_registered_user_can_login(self):
        registration_response = self.client.post(
            reverse("register"),
            {
                "username": "login_candidate_15",
                "email": "login15@example.com",
                "phone": "9876543210",
                "password": "StrongPass123!",
                "role": "candidate",
            },
            format="json",
        )

        self.assertEqual(
            registration_response.status_code,
            status.HTTP_201_CREATED,
        )

        login_response = self.client.post(
            reverse("login"),
            {
                "username": "login_candidate_15",
                "password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(
            login_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("access", login_response.data)
        self.assertIn("refresh", login_response.data)



class RolePermissionTests(APITestCase):

    def setUp(self):
        User = get_user_model()

        self.employer = User.objects.create_user(
            username="rbac_employer",
            email="rbac_employer@example.com",
            password="StrongPass123!",
            role="employer",
        )

        self.candidate = User.objects.create_user(
            username="rbac_candidate",
            email="rbac_candidate@example.com",
            password="StrongPass123!",
            role="candidate",
        )

    def test_candidate_cannot_create_employer_job(self):
        self.client.force_authenticate(user=self.candidate)

        response = self.client.post(
            "/api/employer/job/create/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_employer_cannot_submit_candidate_application(self):
        self.client.force_authenticate(user=self.employer)

        response = self.client.post(
            "/api/candidate/apply/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 403)


class AdminPermissionTests(APITestCase):

    def setUp(self):
        User = get_user_model()

        self.admin = User.objects.create_user(
            username="rbac_admin",
            email="rbac_admin@example.com",
            password="StrongPass123!",
            role="admin",
        )

        self.employer = User.objects.create_user(
            username="admin_test_employer",
            email="admin_test_employer@example.com",
            password="StrongPass123!",
            role="employer",
        )

    def test_admin_can_list_users(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get("/api/admin/user/")

        self.assertEqual(response.status_code, 200)

    def test_employer_cannot_list_users(self):
        self.client.force_authenticate(user=self.employer)

        response = self.client.get("/api/admin/user/")

        self.assertEqual(response.status_code, 403)



class JobOwnershipTests(APITestCase):

    def setUp(self):
        User = get_user_model()

        self.employer_user = User.objects.create_user(
            username="job_owner",
            email="job_owner@example.com",
            password="StrongPass123!",
            role="employer",
        )

        self.other_employer_user = User.objects.create_user(
            username="other_owner",
            email="other_owner@example.com",
            password="StrongPass123!",
            role="employer",
        )

        self.admin_user = User.objects.create_user(
            username="job_admin",
            email="job_admin@example.com",
            password="StrongPass123!",
            role="admin",
        )

        
        self.employer_profile, _ = Employer.objects.get_or_create(
            user=self.employer_user,
            defaults={
                "company_name": "Owner Company",
                "company_mail": "owner-company@example.com",
            },
        )

        self.other_employer_profile, _ = Employer.objects.get_or_create(
            user=self.other_employer_user,
            defaults={
                "company_name": "Other Company",
                "company_mail": "other-company@example.com",
            },
        )


        self.job = Job.objects.create(
            employer=self.employer_profile,
            title="Python Developer",
            department="Engineering",
            location="Remote",
            salary="50000.00",
        )

        self.job_url = f"/api/job/{self.job.pk}/"

    def test_owner_can_retrieve_own_job(self):
        self.client.force_authenticate(user=self.employer_user)

        response = self.client.get(self.job_url)

        self.assertEqual(response.status_code, 200)

    def test_other_employer_cannot_update_job(self):
        self.client.force_authenticate(user=self.other_employer_user)

        response = self.client.patch(
            self.job_url,
            {"title": "Unauthorized Update"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

        self.job.refresh_from_db()
        self.assertEqual(self.job.title, "Python Developer")

    def test_admin_can_retrieve_job(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.job_url)

        self.assertEqual(response.status_code, 200)
