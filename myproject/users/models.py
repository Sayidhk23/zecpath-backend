from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class CustomUser(AbstractUser):
    ADMIN = 'admin'
    EMPLOYER = 'employer'
    CANDIDATE = 'candidate'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (EMPLOYER, 'Employer'),
        (CANDIDATE, 'Candidate'),
    ]


    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.email


def validate_resume(file):
    allowed_extensions = ['.pdf', '.doc', '.docx']
    max_size = 5 * 1024 * 1024
    file_name= file.name.lower()

    if not any(file_name.endswith(ext) for ext in allowed_extensions):
        raise ValidationError(
            'Only pdf, doc and docx files are allowed.'
        )

    if file.size > max_size:
        raise ValidationError(
            'Resume file size must not exceed 5 MB.'
        )



class Candidate(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='candidate_profile')
    skills = models.TextField(blank=True)
    education = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    expected_salary =models.DecimalField( max_digits=12, decimal_places=2, null=True, blank=True)
    resume = models.FileField(upload_to='resume/', blank=True, null=True, validators=[validate_resume])
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email


class Employer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employer_profile')
    company_name = models.CharField(max_length=150)
    company_mail = models.EmailField()
    company_description = models.TextField(blank=True)
    domain= models.CharField(max_length=150, blank=True)
    company_size = models.PositiveIntegerField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name