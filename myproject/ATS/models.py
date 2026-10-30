from django.db import models
from django.conf import settings
from users.models import Employer, Candidate

      
class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ("full_time", "Full-time"),
        ("part_time", "Part-time"),
        ("contract", "Contract"),
        ("internship", "Internship"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("closed", "Closed"),
    ]
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name='job')
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True, default="")
    department = models.TextField()
    skills = models.TextField()
    min_experience = models.PositiveIntegerField(default=0)
    max_experience = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=250)
    salary_min = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True
    )
    salary_max = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True
    )
    job_type = models.CharField(max_length=20,choices=JOB_TYPE_CHOICES,default="full_time")
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="draft")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(
                fields=["status", "is_active", "-created_at"],
                name="job_public_listing_idx"
            ),
            models.Index(
                fields=["job_type", "status", "is_active"],
                name="job_type_status_idx"
            ),
            models.Index(
                fields=["location"],
                name="job_location_idx"
            ),
        ]
    

    def __str__(self):
            return self.title



class Application(models.Model):
    STATUS_CHOICES = [
        ("applied", "Applied"),
        ("under_review", "Under Review"),
        ("shortlisted", "Shortlisted"),
        ("interview", "Interview Scheduled"),
        ("rejected", "Rejected"),
        ("offered", "Offered"),
        ("selected", "Selected"),
    ]
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='application')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='application')
    resume_snapshot = models.FileField( upload_to="application_resumes/", blank=True, null=True )
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='applied')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["candidate", "job"],
                name="unique_candidate_job_application"
            )
        ]

    def __str__(self):
            return f"{self.candidate} - {self.job}"


class ApplicationStatusHistory(models.Model):

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="status_history")
    old_status = models.CharField( max_length=50, blank=True, default="")
    new_status = models.CharField(max_length=50)
    changed_by = models.ForeignKey("users.CustomUser", on_delete=models.SET_NULL, null=True, blank=True, related_name="application_status_changes")
    changed_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return (
            f"Application {self.application_id}: "
            f"{self.old_status} -> {self.new_status}"
        )
