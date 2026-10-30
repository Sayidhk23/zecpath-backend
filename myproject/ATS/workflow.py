from rest_framework.exceptions import ValidationError
from ATS.models import Application

# Define all allowed status transitions.
ALLOWED_TRANSITIONS = {
    "applied": ["under_review", "shortlisted", "rejected"],
    "under_review": ["shortlisted", "rejected"],
    "shortlisted": ["interview", "rejected"],
    "interview": ["offered", "selected", "rejected"],
    "offered": ["selected", "rejected"],
    "selected": [],
    "rejected": [],
}


def validate_status_transition(current_status, new_status):

    # Normalize existing status capitalization.
    current_status = current_status.lower()
    new_status = new_status.lower()

    valid_statuses = dict(Application.STATUS_CHOICES)

    if new_status not in valid_statuses:
        raise ValidationError({
            "status": "Invalid application status."
        })

    allowed_statuses = ALLOWED_TRANSITIONS.get(current_status, [])

    if new_status not in allowed_statuses:
        raise ValidationError({
            "status": (
                f"Cannot change status from "
                f"'{current_status}' to '{new_status}'."
            )
        })

    return True