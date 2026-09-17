from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Job
from .serializers import JobSerializer

class JobListAPI(APIView):

    def get(self, request):
        Jobs = Job.objects.all()
        serializer = JobSerializer(Jobs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request):
        serializer = JobSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.error,
            status=status.HTTP_400_BAD_REQUEST
        )


class UserTestAPI(APIView):
    def get(self, request):
        return Response(
            {
            "message": "User API is working",
            "User" : "Test User"
        },
        status=status.HTTP_200_OK
        )

        
