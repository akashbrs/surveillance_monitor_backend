import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from google.oauth2 import id_token
from django.core.mail import send_mail
from django.conf import settings
from .models import OTPChallenge
from google.auth.transport import requests
import requests as sync_requests

# Optional: Set this to your actual Google Client ID from Google Cloud Console
GOOGLE_CLIENT_ID = "76659038293-5ojfhp80aubesktpfhs45v0crqs3ljej.apps.googleusercontent.com"

class GoogleLoginView(APIView):
    def post(self, request):
        token = request.data.get('token')
        print(f"--- [DEBUG: Google Login Attempt with token: {token[:10]}... ] ---")
        if not token:
            return Response({'error': 'No token provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify Google Token via userinfo endpoint (since frontend returns access_token)
            user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
            response = sync_requests.get(user_info_url, headers={'Authorization': f'Bearer {token}'})

            if response.status_code != 200:
                print("Google API Error:", response.text)
                return Response({'error': 'Failed to fetch user info from Google'}, status=status.HTTP_400_BAD_REQUEST)

            idinfo = response.json()

            # Typical fields: 'email', 'name', 'sub'
            email = idinfo.get('email')
            name = idinfo.get('name', 'User')

            if not email:
                return Response({'error': 'Google token did not provide an email address'}, status=status.HTTP_400_BAD_REQUEST)

            # Get or create user
            user, created = User.objects.get_or_create(username=email, defaults={'email': email, 'first_name': name})

            # Create JWT
            refresh = RefreshToken.for_user(user)

            return Response({
                'data': {
                    'token': str(refresh.access_token),
                    'user': {
                        'email': user.email,
                        'name': user.first_name,
                        'role': 'admin' # Defaulting to admin for Core Sentinel UI
                    }
                }
            })

        except Exception as e:
            return Response({'error': f'Invalid token processing: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # Use email as username since we store it that way
        print(f"--- [DEBUG: Login Attempt for email: {email} ] ---")
        user = authenticate(username=email, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'data': {
                    'token': str(refresh.access_token),
                    'user': {
                        'email': user.email,
                        'name': user.first_name,
                        'role': 'admin' # Defaulting to admin for demo
                    }
                }
            })

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class SignupView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        name = request.data.get('name', 'User')

        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=email).exists():
            print(f"--- [DEBUG: Signup Failed - User {email} already exists ] ---")
            return Response({'error': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        print(f"--- [DEBUG: Creating new user: {email} ({name}) ] ---")
        user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'data': {
                'token': str(refresh.access_token),
                'user': {
                    'email': user.email,
                    'name': user.first_name,
                    'role': 'admin'
                }
            }
        }, status=status.HTTP_201_CREATED)


class SendOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user.email:
            return Response({'error': 'User has no email associated'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate OTP
        otp_challenge = OTPChallenge.generate_otp(user)
        print(f"--- [DEV DEBUG: OTP sent to {user.email}: {otp_challenge.otp} ] ---")

        # Send Email via Google SMTP
        try:
            send_mail(
                subject='Your Core Sentinel 2FA Code',
                message=f'Welcome back. Your 6-digit Core Sentinel security code is: {otp_challenge.otp}.\n\nThis code will expire in 10 minutes.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return Response({'success': True, 'message': 'OTP sent successfully to your email.'})
        except Exception as e:
            return Response({'error': f'Failed to send email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        otp_code = request.data.get('otp', '').strip()

        print(f"DEBUG: Verifying OTP for user: {user.username} (ID: {user.id})")
        print(f"DEBUG: Received OTP from frontend: '{otp_code}'")

        if not otp_code:
            print("DEBUG: Empty OTP provided")
            return Response({'error': 'No OTP provided'}, status=status.HTTP_400_BAD_REQUEST)

        challenge = OTPChallenge.objects.filter(user=user, otp=otp_code).last()
        
        if not challenge:
            print(f"DEBUG: No challenge found for user {user.username} with OTP {otp_code}")
            # Let's see what the latest challenge IS
            latest = OTPChallenge.objects.filter(user=user).last()
            if latest:
                print(f"DEBUG: Latest actual OTP for this user is: {latest.otp}")
            else:
                print("DEBUG: No OTP challenges found at all for this user")
            return Response({'error': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        if challenge.is_valid():
            print("DEBUG: OTP is valid! Marking as verified.")
            challenge.is_verified = True
            challenge.save()
            return Response({'success': True, 'message': 'OTP verified.'})
        
        print(f"DEBUG: Challenge found but is_valid() returned False. Created at: {challenge.created_at}")
        return Response({'error': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Logout is handled client-side by deleting the JWT token.
        This endpoint exists to satisfy the frontend constant and provide a clean exit.
        """
        return Response({"success": True, "message": "Logged out successfully."})

