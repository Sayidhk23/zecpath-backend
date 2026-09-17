from django.urls import path
from .views import JobListAPI, UserTestAPI

urlpatterns = [
    path('job/', JobListAPI.as_view(), name= 'job-list'),
    path('user-test/', UserTestAPI.as_view(), name='user-test'),
]