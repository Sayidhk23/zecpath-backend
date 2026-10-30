from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from.views import RegisterAPI, LoginAPI, LogoutAPI, ProfileAPI, CandidateProfileAPI, EmployerProfileAPI, ResumeUploadAPI
urlpatterns = [
    path('register/',RegisterAPI.as_view(), name='register'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('logout/', LogoutAPI.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileAPI.as_view(), name='profile'),
    path('candidate/profile/', CandidateProfileAPI.as_view(), name='candidate-profile'),
    path('employer/profile/', EmployerProfileAPI.as_view(), name='employer-profile'),
    path('candidate/resume/', ResumeUploadAPI.as_view(), name='candidate-resume'),
]
