from rest_framework import serializers
from .models import Job , Application

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields= '__all__'
        read_only_fields = [
            "id",
            "employer",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        min_exp = attrs.get(
            "min_experience",
            getattr(self.instance, "min_experience", 0)
        )
        max_exp = attrs.get(
            "max_experience",
            getattr(self.instance, "max_experience", 0)
        )

        if min_exp > max_exp:
            raise serializers.ValidationError({
                "max_experience":
                    "Maximum experience must be greater than or equal to minimum experience."
            })

        min_salary = attrs.get(
            "salary_min",
            getattr(self.instance, "salary_min", None)
        )
        max_salary = attrs.get(
            "salary_max",
            getattr(self.instance, "salary_max", None)
        )

        if (
            min_salary is not None
            and max_salary is not None
            and min_salary > max_salary
        ):
            raise serializers.ValidationError({
                "salary_max":
                    "Maximum salary must be greater than or equal to minimum salary."
            })

        return attrs


class ApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(
        source="job.title",
        read_only=True
    )

    class Meta:
        model = Application
        fields = [
            "id",
            "candidate",
            "job",
            "job_title",
            "resume_snapshot",
            "status",
            "applied_at",
        ]
        read_only_fields = [
            "id",
            "candidate",
            "resume_snapshot",
            "status",
            "applied_at",
        ]