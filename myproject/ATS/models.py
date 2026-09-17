from django.db import models
from django.contrib.auth.models import User


class Employer(models.Model):
      user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer')
      company_name = models.CharField(max_length=150)
      company_mail = models.EmailField()
      company_discription = models.TextField(blank=True)
      created_at = models.DateTimeField(auto_now_add=True)

      def __str__(self):
            return self.company_name


class Candidate(models.Model):
      user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate')
      phone = models.CharField(max_length=20)
      resume = models.FileField(upload_to='resume/', null=True, blank=True)
      skills = models.TextField(blank=True)
      created_at = models.DateTimeField(auto_now_add=True)

      def __str__(self):
            return self.user.username
      

class Job(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name='job')
    title = models.CharField(max_length=250)
    department = models.TextField()
    location = models.CharField(max_length=250)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    

    def __str__(self):
            return self.title



class Application(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='application')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='application')
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Applied')

    def __str__(self):
            return f"{self.candidate} - {self.job}"
