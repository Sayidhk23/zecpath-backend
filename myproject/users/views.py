from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer, CandidateProfileSerializer, EmployerProfileSerializer

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Candidate, Employer

from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterAPI(generics.CreateAPIView):

    queryset = User.objects.all()

    serializer_class = RegisterSerializer

    permission_classes = [AllowAny]



class LoginAPI(TokenObtainPairView):

    permission_classes = [AllowAny]




class LogoutAPI(APIView):

    permission_classes= [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required '},
                status= status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {'message': 'Logout successful.'},
                status=status.HTTP_200_OK
            )

        except TokenError:
            return Response(
                {'error': 'Invalid or expired refresh token.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ProfileAPI(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
        })

class CandidateProfileAPI(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        if request.user.role == User.ADMIN:
            profile = Candidate.objects.filter(is_deleted=False)
            serializer = CandidateProfileSerializer(
                profile,
                many=True
            )

            return Response(serializer.data)

        if request.user.role != User.CANDIDATE:
            return Response(
                {
                    'error: only candidate can access.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            profile = Candidate.objects.get(
                user= request.user,
                is_deleted= False
            )
        except Candidate.DoesNotExist:
            return Response(
                {
                    'error: candidate profile cannot found.'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = CandidateProfileSerializer(profile)

        return Response(serializer.data)


    def put(self, request):

        if request.user.role == User.ADMIN:

            profile_id = request.data.get('profile_id')

            if not profile_id:
                return Response(
                    {
                        'error': 'profile_id is required for admin.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                profile = Candidate.objects.get(
                    id=profile_id,
                    is_deleted=False
                )
            except Candidate.DoesNotExist:
                return Response(
                    {
                        'error': 'Candidate profile not found.'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

        elif request.user.role == User.CANDIDATE:

            try:
                profile = Candidate.objects.get(
                    user=request.user,
                    is_deleted=False
                )
            except Candidate.DoesNotExist:
                return Response(
                    {
                        'error': 'Candidate profile not found.'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

        else:
            return Response(
                {
                    'error': 'You do not have permission to update this profile.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CandidateProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


    def delete(self, request):
        if request.user.role != User.CANDIDATE:
            return Response(
                {
                    'error': 'Only candidates can delete their profile.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            profile = Candidate.objects.get(
                user=request.user,
                is_deleted=False
            )
        except Candidate.DoesNotExist:
            return Response(
                {
                    'error': 'Candidate profile not found.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        profile.is_deleted = True
        profile.save()

        return Response(
            {
                'message': 'Candidate profile deleted successfully.'
            },
            status=status.HTTP_200_OK
        )

        


class EmployerProfileAPI(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        if request.user.role == User.ADMIN:
            profiles = Employer.objects.filter(is_deleted=False)

            serializer = EmployerProfileSerializer(
                profiles,
                many=True
            )

            return Response(serializer.data)

        if request.user.role != User.EMPLOYER:
            return Response(
                {
                    'error': 'Only employers can access this profile.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            profile = Employer.objects.get(
                user=request.user,
                is_deleted=False
            )
        except Employer.DoesNotExist:
            return Response(
                {
                    'error': 'Employer profile not found.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = EmployerProfileSerializer(profile)

        return Response(serializer.data)

    def put(self, request):

        if request.user.role == User.ADMIN:

            profile_id = request.data.get('profile_id')

            if not profile_id:
                return Response(
                    {
                        'error': 'profile_id is required for admin.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                profile = Employer.objects.get(
                    id=profile_id,
                    is_deleted=False
                )
            except Employer.DoesNotExist:
                return Response(
                    {
                        'error': 'Employer profile not found.'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

        elif request.user.role == User.EMPLOYER:

            try:
                profile = Employer.objects.get(
                    user=request.user,
                    is_deleted=False
                )
            except Employer.DoesNotExist:
                return Response(
                    {
                        'error': 'Employer profile not found.'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

        else:
            return Response(
                {
                    'error': 'You do not have permission to update this profile.'
                },
                    status=status.HTTP_403_FORBIDDEN
            )

        serializer = EmployerProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request):

        if request.user.role != User.EMPLOYER:
            return Response(
                {
                    'error': 'Only employers can delete their profile.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            profile = Employer.objects.get(
                user=request.user,
                is_deleted=False
            )
        except Employer.DoesNotExist:
            return Response(
                {
                    'error': 'Employer profile not found.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        profile.is_deleted = True
        profile.save()

        return Response(
            {
                'message': 'Employer profile deleted successfully.'
            },
            status=status.HTTP_200_OK
        )


class ResumeUploadAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        # Get candidate profile
        try:
            candidate = request.user.candidate_profile
        except Candidate.DoesNotExist:
            return Response(
                {"error": "Candidate profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check whether file was provided
        if 'resume' not in request.FILES:
            return Response(
                {"error": "Please upload a resume."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate resume using serializer
        serializer = CandidateProfileSerializer(
            candidate,
            data=request.data,
            partial=True
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Delete old resume only AFTER new file passes validation
        if candidate.resume:
            candidate.resume.delete(save=False)

        # Save new resume
        serializer.save()

        return Response(
            {
                "message": "Resume uploaded successfully.",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )
