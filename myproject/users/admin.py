from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Candidate, Employer


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        (
            'Additional Information',
            {
                'fields': (
                    'phone',
                    'role',
                    'is_verified',
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            'Additional Information',
            {
                'fields': (
                    'email',
                    'phone',
                    'role',
                    'is_verified',
                )
            },
        ),
    )

    list_display = (
        'username',
        'email',
        'role',
        'is_verified',
        'is_active',
    )

    list_filter = (
        'role',
        'is_verified',
        'is_active',
        'is_staff',
    )

    search_fields = (
        'username',
        'email',
        'phone',
    )

    ordering = ('email',)


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):

    list_display = (
        'user',
    )

    search_fields = (
        'username',
        'email',
        
    )


@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):

    list_display = (
        'user',
    )

    search_fields = (
        'company_name',
        'company_mail',
    )