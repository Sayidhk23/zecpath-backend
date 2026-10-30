from django.urls import path
from .views import JobListAPI, EmployerJobCreateAPI, CandidateApplyAPI, AdminUserListAPI, JobDetailAPI, EmployerJobStatusAPI, FeaturedJobListAPI, LatestJobListAPI, MyApplicationHistoryAPI, ApplicationDetailAPI, ApplicationStatusUpdateAPI

urlpatterns = [
    path('job/', JobListAPI.as_view(), name= 'job-list'),
     path(
        'job/<int:pk>/',
        JobDetailAPI.as_view(),
        name='job-detail',
    ),
    path('employer/job/create/', EmployerJobCreateAPI.as_view(), name='employer-job-create'),
    path('candidate/apply/', CandidateApplyAPI.as_view(), name='candidate-apply'),
    path('admin/user/', AdminUserListAPI.as_view(), name='admin-user'),
    path("job/<int:pk>/status/",EmployerJobStatusAPI.as_view(), name="employer-job-status"),
    path("job/featured/",FeaturedJobListAPI.as_view(),name="featured-jobs"),
    path("job/latest/", LatestJobListAPI.as_view(), name="latest-jobs"),
    path("application/my/", MyApplicationHistoryAPI.as_view(), name="my-application-history"),
    path("application/<int:application_id>/", ApplicationDetailAPI.as_view(), name="application-details"),
    path("application/<int:application_id>/status/", ApplicationStatusUpdateAPI.as_view(), name="application-status-update")
]