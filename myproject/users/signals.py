from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomUser, Candidate, Employer


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):

    if created:

        if instance.role == CustomUser.CANDIDATE:
            Candidate.objects.create(
                user=instance
            )

        elif instance.role == CustomUser.EMPLOYER:
            Employer.objects.create(
                user=instance,
                company_name="",
                company_mail=instance.email
            )