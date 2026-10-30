from django.shortcuts import render, get_object_or_404
from django.db import IntegrityError, transaction
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .pagination import JobPagination
from rest_framework.exceptions import ValidationError

from .models import Job, Application, ApplicationStatusHistory
from .serializers import JobSerializer, ApplicationSerializer
from services.job_service import create_job
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import  IsJobOwnerOrAdmin
from users.permissions import IsAdmin, IsCandidate, IsEmployer
from django.contrib.auth import get_user_model
from django.db.models import Q
from ATS.workflow import validate_status_transition

User = get_user_model()



class JobListAPI(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        if self.request.method == "POST":
            return [IsAuthenticated(), IsEmployer()]

        return [IsAuthenticated()]

    def get(self, request):
        # Show only active, published jobs
        jobs = Job.objects.filter(
            status="published",
            is_active=True
        ).select_related(
            "employer"
        ).order_by("-created_at")

        # Filter by keyword
        search_term = request.query_params.get("search")

        if search_term:
            jobs = jobs.filter(
                Q(title__icontains=search_term)
                | Q(description__icontains=search_term)
                | Q(department__icontains=search_term)
                | Q(location__icontains=search_term)
                | Q(skills__icontains=search_term)
            )

        # Filter by skills
        skills = request.query_params.get("skills")

        if skills:
            skill_list = [
                skill.strip()
                for skill in skills.split(",")
                if skill.strip()
            ]

            for skill in skill_list:
                jobs = jobs.filter(
                    skills__icontains=skill
                )

        # Filter by location
        location = request.query_params.get("location")

        if location:
            jobs = jobs.filter(
                location__icontains=location
            )

        # Filter by job type
        job_type = request.query_params.get("job_type")

        if job_type:
            jobs = jobs.filter(
                job_type=job_type
            )

        # Filter by minimum required experience
        min_exp = request.query_params.get("min_experience")

        if min_exp is not None:
            try:
                min_exp = int(min_exp)

                if min_exp < 0:
                    return Response(
                        {"error": "Experience cannot be negative."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                jobs = jobs.filter(
                    max_experience__gte=min_exp
                )

            except ValueError:
                return Response(
                    {"error": "min_experience must be an integer."},
                    status=status.HTTP_400_BAD_REQUEST
                )


        # Filter by maximum required experience
        max_exp = request.query_params.get("max_experience")

        if max_exp is not None:
            try:
                max_exp = int(max_exp)

                if max_exp < 0:
                    return Response(
                        {"error": "Experience cannot be negative."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                jobs = jobs.filter(
                    min_experience__lte=max_exp
                )

            except ValueError:
                return Response(
                    {"error": "max_experience must be an integer."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Filter by minimum salary
        min_salary = request.query_params.get("min_salary")

        if min_salary is not None:
            try:
                min_salary = float(min_salary)

                if min_salary < 0:
                    return Response(
                        {"error": "Salary cannot be negative."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                jobs = jobs.filter(
                    salary_max__gte=min_salary
                )

            except ValueError:
                return Response(
                    {"error": "min_salary must be a number."},
                    status=status.HTTP_400_BAD_REQUEST
                )


        # Filter by maximum salary
        max_salary = request.query_params.get("max_salary")

        if max_salary is not None:
            try:
                max_salary = float(max_salary)

                if max_salary < 0:
                    return Response(
                        {"error": "Salary cannot be negative."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                jobs = jobs.filter(
                    salary_min__lte=max_salary
                )

            except ValueError:
                return Response(
                    {"error": "max_salary must be a number."},
                    status=status.HTTP_400_BAD_REQUEST
                )    

        # Pagination
        paginator = JobPagination()
        

        paginated_jobs = paginator.paginate_queryset(
            jobs,
            request,
            view=self
        )

        serializer = JobSerializer(
            paginated_jobs,
            many=True
        )

        return paginator.get_paginated_response(
            serializer.data
        )


    def post(self, request):
        serializer = JobSerializer(data=request.data)

        if serializer.is_valid():
            jobs = create_job(serializer.validated_data)
            return Response(
                JobSerializer(jobs).data,
                status=status.HTTP_201_CREATED
            )
        return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
        )

class FeaturedJobListAPI(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Job.objects.filter(
            status="published",
            is_active=True,
            is_featured=True
        ).select_related(
            "employer"
        ).order_by("-created_at")

class LatestJobListAPI(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Job.objects.filter(
            status="published",
            is_active=True
        ).select_related(
            "employer"
        ).order_by("-created_at")[:10]


class EmployerJobCreateAPI(generics.CreateAPIView):
    queryset= Job.objects.all()
    serializer_class= JobSerializer
    permission_classes= [
        IsAuthenticated,
        IsEmployer
    ]
    def perform_create(self, serializer):
        serializer.save(
            employer = self.request.user.employer_profile
        )
        

class CandidateApplyAPI(generics.CreateAPIView):
    serializer_class = ApplicationSerializer

    permission_classes = [
        IsAuthenticated,
        IsCandidate,
    ]

    def get_queryset(self):
        return Application.objects.filter(
            candidate=self.request.user.candidate_profile
        )

    def perform_create(self, serializer):

        candidate = self.request.user.candidate_profile

        # 1. Get the job ID from the request
        job_id = self.request.data.get("job")

        if not job_id:
            raise ValidationError({
                "job": "Job ID is required."
            })

        # 2. Check whether the job exists
        try:
            job = Job.objects.get(id=job_id)
        except (Job.DoesNotExist, ValueError, TypeError):
            raise ValidationError({
                "job": "Invalid job ID or job not found."
            })

        # 3. Check whether the job accepts applications
        if job.status != "published" or not job.is_active:
            raise ValidationError({
                "job": "This job is not accepting applications."
            })

        # 4. Prevent duplicate applications
        if Application.objects.filter(
            candidate=candidate,
            job=job
        ).exists():
            raise ValidationError({
                "job": "You have already applied for this job."
            })

        # 5. Create a separate resume snapshot
        resume_snapshot = None

        if candidate.resume:
            import os
            import uuid

            extension = os.path.splitext(candidate.resume.name)[1]

            candidate.resume.open("rb")

            try:
                resume_content = candidate.resume.read()
            finally:
                candidate.resume.close()

            resume_snapshot = ContentFile(
                resume_content,
                name=f"{uuid.uuid4().hex}{extension}"
            )

        # 6. Save the application
        try:
            with transaction.atomic():
                serializer.save(
                    candidate=candidate,
                    job=job,
                    resume_snapshot=resume_snapshot,
                    status="applied"
                )
        except IntegrityError:
            if resume_snapshot:
                resume_snapshot.close()

            raise ValidationError({
                "job": "You have already applied for this job."
            })

class AdminUserListAPI(APIView):
    permission_classes= [
        IsAuthenticated,
        IsAdmin
    ]
    def get(self, request):
        users = User.objects.all()

        data = [
            {
                'id': user.id,
                'email':user.email,
                'role': user.role,
                'is_active':user.is_active,
            }
            for user in users
        ]

        return Response(data, status=status.HTTP_200_OK)


class JobDetailAPI(generics.RetrieveUpdateDestroyAPIView):

    queryset = Job.objects.all()
    serializer_class = JobSerializer

    permission_classes = [
        IsAuthenticated,
        IsJobOwnerOrAdmin,
    ]


class EmployerJobStatusAPI(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def patch(self, request, pk):
        try:
            job = Job.objects.get(
                pk=pk,
                employer=request.user.employer_profile
            )
        except Job.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Job not found or you do not own this job."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        is_active = request.data.get("is_active")

        if not isinstance(is_active, bool):
            return Response(
                {
                    "success": False,
                    "message": "is_active must be true or false."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        job.is_active = is_active
        job.save(update_fields=["is_active", "updated_at"])

        return Response(
            {
                "success": True,
                "message": (
                    "Job activated successfully."
                    if is_active
                    else "Job deactivated successfully."
                ),
                "job_id": job.id,
                "is_active": job.is_active
            },
            status=status.HTTP_200_OK
        )


class MyApplicationHistoryAPI(generics.ListAPIView):

    serializer_class = ApplicationSerializer

    permission_classes = [
        IsAuthenticated,
        IsCandidate,
    ]

    def get_queryset(self):
        return (
            Application.objects
            .filter(
                candidate=self.request.user.candidate_profile
            )
            .select_related("job", "candidate")
            .order_by("-applied_at")
        )

class ApplicationDetailAPI(generics.RetrieveAPIView):

    serializer_class = ApplicationSerializer

    permission_classes = [
        IsAuthenticated,
        IsCandidate,
    ]

    lookup_url_kwarg = "application_id"

    def get_queryset(self):
        print("Logged-in user:", self.request.user.id)
        print("Candidate profile:", self.request.user.candidate_profile.id)
        return (
            Application.objects
            .filter(
                candidate=self.request.user.candidate_profile
            )
            .select_related("job", "candidate")
        )

class ApplicationStatusUpdateAPI(APIView):

    permission_classes = [IsAuthenticated, IsEmployer]

    def patch(self, request, application_id):

        new_status = request.data.get("status")
        note = request.data.get("note", "")

        if not new_status:
            return Response(
                {
                    "success": False,
                    "message": "Status is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():

            application = get_object_or_404(
                Application.objects.select_for_update().select_related(
                    "job",
                    "job__employer"
                ),
                id=application_id
            )

            # Verify that the logged-in employer owns this job.
            if application.job.employer.user_id != request.user.id:
                return Response(
                    {
                        "success": False,
                        "message": "You cannot update applications for another employer's job."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            old_status = application.status

            # Validate the requested transition.
            validate_status_transition(
                old_status,
                new_status
            )

            # Update the application.
            application.status = new_status
            application.save(update_fields=["status"])

            # Record the status change.
            ApplicationStatusHistory.objects.create(
                application=application,
                old_status=old_status,
                new_status=new_status,
                changed_by=request.user,
                note=note
            )

        return Response(
            {
                "success": True,
                "message": "Application status updated successfully.",
                "application_id": application.id,
                "old_status": old_status,
                "new_status": new_status
            },
            status=status.HTTP_200_OK
        )