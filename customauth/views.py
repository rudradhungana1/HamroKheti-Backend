import os
from tokenize import TokenError

from dj_rest_auth.serializers import TokenSerializer
from django.http import JsonResponse
from django.contrib.auth import authenticate, get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from hamrokheti import settings
from users.models import User
from .serializers import LoginSerializer
import jwt
from datetime import datetime, timedelta


class LoginView(APIView):
    @method_decorator(csrf_exempt)  # Disabling CSRF for login view
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)

            if user:
                if user.status == "locked":
                    return JsonResponse({
                        "status": "FAILURE",
                        "message": "Your account is locked. Please contact the administrator."
                    }, status=400)
                # Calculate expiry time
                expiry_time = datetime.utcnow() + timedelta(hours=24)

                # # Generate JWT token with expiry time
                # token = jwt.encode({'username': user.username, 'email': user.email, 'user_role': user.user_role,
                #                         'exp': expiry_time}, os.environ.get('SECRET_KEY'), algorithm='HS256')
                token = AccessToken.for_user(user)

                # Get profile image based on user's role
                profile_image = None
                full_name = None
                if user.user_role == 'farmer' and hasattr(user, 'farmer_profile'):
                    profile_image = user.farmer_profile.profile_image
                    full_name = user.farmer_profile.full_name
                elif user.user_role == 'partner' and hasattr(user, 'partner_profile'):
                    profile_image = user.partner_profile.profile_image
                    full_name = user.partner_profile.full_name
                elif user.user_role == 'normal_user' and hasattr(user, 'profile'):
                    profile_image = user.profile.profile_image
                    full_name = user.profile.full_name

                # Set JWT token in cookie with expiry time
                response = JsonResponse({
                    "status": "SUCCESS",
                    "message": "Successfully Logged in",
                    "accessToken": str(token),
                    "userData": {
                        "username": user.username,
                        "email": user.email,
                        "user_role": user.user_role,
                        "id": user.id,
                        "profile_image": profile_image,
                        "full_name": full_name
                    }
                })

                response.set_cookie('jwt', token, expires=expiry_time, httponly=True)

                return response
            else:
                return JsonResponse({"status": "FAILURE", "message": "Invalid credentials"}, status=401)
        else:
            return JsonResponse({"status": "FAILURE", "message": "Invalid input data"}, status=400)


class ValidateTokenView(APIView):
    @method_decorator(csrf_exempt)
    def post(self, request):
        token = request.data.get('token')
        if not token:
            return JsonResponse({"status": "FAILURE", "message": "Token is missing"}, status=400)

        try:
            # Attempt to verify the token
            decoded_token = AccessToken(token)
            user_id = decoded_token.payload['user_id']
            user = get_user_model().objects.get(pk=user_id)

            # Get profile image based on user's role
            profile_image = None
            full_name = None
            if user.user_role == 'farmer' and hasattr(user, 'farmer_profile'):
                profile_image = user.farmer_profile.profile_image
                full_name = user.farmer_profile.full_name
            elif user.user_role == 'partner' and hasattr(user, 'partner_profile'):
                profile_image = user.partner_profile.profile_image
                full_name = user.partner_profile.full_name
            elif user.user_role == 'normal_user' and hasattr(user, 'profile'):
                profile_image = user.profile.profile_image
                full_name = user.profile.full_name

            return JsonResponse({"status": "SUCCESS", "message": "Token is valid", "userData": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "user_role": user.user_role,
                "profile_image": profile_image,
                "full_name": full_name
            }})

        except TokenError as e:
            # Token is either expired or invalid
            return JsonResponse({"status": "FAILURE", "message": str(e)}, status=401)
        except get_user_model().DoesNotExist:
            # User with the provided ID doesn't exist
            return JsonResponse({"status": "FAILURE", "message": "User does not exist"}, status=404)