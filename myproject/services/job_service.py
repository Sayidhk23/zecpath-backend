from ATS.models import Job

def create_job(data):
    return Job.objects.create(**data)
