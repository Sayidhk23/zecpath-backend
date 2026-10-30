from rest_framework import serializers
from django.db import transaction
from .models import Candidate, Employer
from django.contrib.auth import get_user_model


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    company_name = serializers.CharField(write_only=True, required=False, allow_blank=False)
    company_mail = serializers.EmailField(write_only=True, required= False)

    role = serializers.ChoiceField(
        choices=User.ROLE_CHOICES,
        required = False
    )

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'phone',
            'password',
            'role',  
            'company_name',
            'company_mail',
        ]

    def validate_email(self, value):
        if User.objects.filter(
            email__iexact=value
            ).exists():
                raise serializers.ValidationError(
                    'Email already registered.'
                )
        return value

    def validate(self, data):
        if data.get('role') == 'employer':
            if not data.get('company_name'):
                raise serializers.ValidationError({
                    'company name':
                    'company name is required for employers'
                })

            if not data.get('company_mail'):
                raise serializers.ValidationError({
                    'company mail':
                    'company mail is required for employer'
                })

        return data

        
    @transaction.atomic
    def create(self, validated_data):
        company_name = validated_data.pop("company_name", None)
        company_mail = validated_data.pop("company_mail", None)
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # The post_save signal creates the profile automatically.
        if user.role == User.EMPLOYER:
            employer = user.employer_profile
            employer.company_name = company_name
            employer.company_mail = company_mail
            employer.save(update_fields=["company_name", "company_mail"])

        return user




class CandidateProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Candidate
        fields = [
            'id',
            'skills',
            'education',
            'experience',
            'expected_salary',
            'resume',
            'is_deleted',
            'created_at',
            'updated_at',
        ]

        read_only_fields=[
            'id',
            'is_deleted',
            'created_at',
            'updated_at',
        ]

    def validate_expected_salary(self, value):

        if value is not None and value < 0:
            raise serializers.ValidationError(
                'Expeted salary cannot be negative'
            )
        return value


class EmployerProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employer
        fields =[
            'id',
            'company_name',
            'company_mail',
            'domain',
            'company_size',
            'is_verified',
            'is_deleted',
            'created_at',
            'updated_at',
        ]

        read_only_fields=[
            'id',
            'is_verified',
            'is_deleted',
            'created_at',
            'updated_at',
        ]

    def validate_company_name(self, value):

        if not value.strip():
            raise serializers.ValidationError(
                'Company name cannot be empty,'
            )
        return value

    def validate_company_size(self, value):
        
        if value is not None and value < 0:
            raise serializers.ValidationError(
                'company size must be greater than 0.'
            )
        return value
