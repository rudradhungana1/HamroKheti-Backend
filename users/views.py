from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import User, UserProfile, FarmerProfile, PartnerProfile
from users.serializers import UserSerializer, UserProfileSerializer, FarmerProfileSerializer, PartnerProfileSerializer, \
    SuperUserSerializer
from utils.combine_error_message import combine_error_messages
from utils.upload_image import upload_image


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @action(methods=['PATCH'], detail=True, url_path='change-status')
    def user_status_change(self, request, pk=None):
        try:
            if not request.user.user_role == 'admin':
                return Response(
                    {
                        "message": "You are not authorized to perform this action",
                        "status": "FAILURE",
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            user = get_object_or_404(User, pk=pk)
            user.status = request.data['status']
            user.save()
            return Response(
                {
                    "message": "USER STATUS CHANGED SUCCESSFULLY",
                    "status": "SUCCESS",
                }
            )
        except Exception as e:
            return Response(
                {
                    "message": str(e),
                    "status": "FAILURE",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def list(self, request):
        try:
            if not request.user.user_role == 'admin':
                return Response(
                    {
                        "message": "You are not authorized to perform this action",
                        "status": "FAILURE",
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(
                {
                    "message": "DATA RETRIEVED SUCCESSFULLY",
                    "status": "SUCCESS",
                    "data": serializer.data,
                }
            )
        except Exception as e:
            return Response(
                {
                    "message": str(e),
                    "status": "FAILURE",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def retrieve(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(user)
            return Response(
                {
                    "message": "DATA RETRIEVED SUCCESSFULLY",
                    "status": "SUCCESS",
                    "data": serializer.data,
                }
            )
        except User.DoesNotExist:
            return Response(
                {
                    "message": "User does not exist",
                    "status": "FAILURE",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def destroy(self, pk=None, **kwargs):
        try:
            user = User.objects.get(pk=pk)
            user.delete()
            return Response(
                {
                    "message": "User deleted successfully",
                    "status": "SUCCESS",
                },
            )
        except User.DoesNotExist:
            return Response(
                {
                    "message": "User does not exist",
                    "status": "FAILURE",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request, **kwargs):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "message": "User created successfully",
                        "status": "SUCCESS",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {
                        "message": combine_error_messages(serializer.errors),
                        "status": "FAILURE",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return Response(
                {
                    "message": str(e),
                    "status": "FAILURE",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=['put'], url_path='update-profile-image')
    def update_image(self, request, pk=None):
        try:
            user_profile = get_object_or_404(UserProfile, user__id=pk, user=request.user)
            if request.user.user_role == 'farmer':
                user_profile = get_object_or_404(FarmerProfile, user__id=pk, user=request.user)

            if 'profile_image' in self.request.data:
                profile_image = self.request.data['profile_image']
                if profile_image:
                    user_profile.profile_image = profile_image
                    user_profile.save()
                    return Response(
                        {
                            "message": "Image updated successfully",
                            "status": "SUCCESS",
                        }, status=status.HTTP_200_OK
                    )
            else:
                return Response(
                    {
                        "message": "No image provided",
                        "status": "FAILURE",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {
                    "message": str(e),
                    "status": "FAILURE",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=['put'], detail=False, url_path='update-profile')
    def update_profile(self, request):
        try:
            user = request.user
            if user.user_role == 'farmer':
                user_profile, created = FarmerProfile.objects.get_or_create(user=user)
                serializer = FarmerProfileSerializer(user_profile, data=request.data, partial=True)
            elif user.user_role == 'partner':
                user_profile, created = PartnerProfile.objects.get_or_create(user=user)
                serializer = PartnerProfileSerializer(user_profile, data=request.data, partial=True)
            else:
                user_profile, created = UserProfile.objects.get_or_create(user=user)
                serializer = UserProfileSerializer(user_profile, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "message": "Profile updated successfully",
                        "status": "SUCCESS",
                        "user": serializer.data
                    }, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        "message": "Validation Error",
                        "status": "FAILURE",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {
                    "message": str(e),
                    "status": "FAILURE",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=['GET'], detail=False, url_path='get-profile')
    def get_profile(self, request):
        try:
            user = request.user
            if user.user_role == 'farmer':
                user_profile = get_object_or_404(FarmerProfile, user=request.user)
                serializer = FarmerProfileSerializer(user_profile)
            elif user.user_role == 'partner':
                user_profile = get_object_or_404(PartnerProfile, user__id=user.id, user=request.user)
                serializer = PartnerProfileSerializer(user_profile)
            else:
                user_profile = get_object_or_404(UserProfile, user__id=user.id, user=request.user)
                serializer = UserProfileSerializer(user_profile)
            return Response(
                {
                    "message": "DATA RETRIEVED SUCCESSFULLY",
                    "status": "SUCCESS",
                    "data": serializer.data,
                }
            )
        except Exception as e:
            return Response(
                {
                    "message": str(e),
                    "status": "FAILURE",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=['GET'], url_path='partners')
    def get_partners(self, request):
        try:
            if request.user.is_authenticated:
                if not request.user.user_role == 'admin':
                    return Response(
                        {
                            "message": "You are not authorized to perform this action",
                            "status": "FAILURE",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                partners = self.queryset.filter(user_role='partner')
                serializer = self.get_serializer(partners, many=True)
                return Response(
                    {
                        "message": "DATA RETRIEVED SUCCESSFULLY",
                        "status": "SUCCESS",
                        "data": serializer.data,
                    }
                )
            else:
                return Response(
                    {
                        "message": "You are not authorized to perform this action",
                        "status": "FAILURE",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {
                    "message": "FAILURE",
                    "status": "FAILURE",
                    "data": str(e),
                }
            )

    @action(methods=['GET'], detail=False, url_path='farmers')
    def get_farmers(self, request):
        try:
            if request.user.is_authenticated:
                if not request.user.user_role == 'admin':
                    return Response(
                        {
                            "message": "You are not authorized to perform this action",
                            "status": "FAILURE",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                farmers = self.queryset.filter(user_role='farmer')
                serializer = self.get_serializer(farmers, many=True)
                return Response(
                    {
                        "message": "DATA RETRIEVED SUCCESSFULLY",
                        "status": "SUCCESS",
                        "data": serializer.data,
                    }
                )
            else:
                return Response(
                    {
                        "message": "You are not authorized to perform this action",
                        "status": "FAILURE",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {
                    "message": "FAILURE",
                    "status": "FAILURE",
                    "data": str(e),
                }
            )

    @action(methods=['GET'], detail=False, url_path='customers')
    def get_customers(self, request):
        try:
            if request.user.is_authenticated:
                if not request.user.user_role == 'admin':
                    return Response(
                        {
                            "message": "You are not authorized to perform this action",
                            "status": "FAILURE",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                customers = self.queryset.filter(user_role='normal_user')
                serializer = self.get_serializer(customers, many=True)
                return Response(
                    {
                        "message": "DATA RETRIEVED SUCCESSFULLY",
                        "status": "SUCCESS",
                        "data": serializer.data,
                    }
                )
            else:
                return Response(
                    {
                        "message": "You are not authorized to perform this action",
                        "status": "FAILURE",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {
                    "message": "FAILURE",
                    "status": "FAILURE",
                    "data": str(e),
                }
            )

    @action(methods=['GET'], detail=False, url_path='admin')
    def get_admin_list(self, request):
        try:
            if request.user.is_authenticated:
                if not request.user.user_role == 'admin':
                    return Response(
                        {
                            "message": "You are not authorized to perform this action",
                            "status": "FAILURE",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                customers = self.queryset.filter(user_role='admin')
                serializer = self.get_serializer(customers, many=True)
                return Response(
                    {
                        "message": "DATA RETRIEVED SUCCESSFULLY",
                        "status": "SUCCESS",
                        "data": serializer.data,
                    }
                )
            else:
                return Response(
                    {
                        "message": "You are not authorized to perform this action",
                        "status": "FAILURE",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {
                    "message": "FAILURE",
                    "status": "FAILURE",
                    "data": str(e),
                }
            )

    @action(methods=['POST'], detail=False, url_path='create-admin')
    def create_admin(self, request):
        try:
            user = request.user
            if user.user_role == 'admin':
                serializer = SuperUserSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        {
                            "message": "User created successfully",
                            "status": "SUCCESS",
                            "data": serializer.data,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response(
                        {
                            "message": "Validation Error",
                            "status": "FAILURE",
                            "errors": serializer.errors,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    {
                        "message": "You are not authorized to perform this action",
                        "status": "FAILURE",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return Response(
                {
                    "message": str(e),
                    "status": "FAILURE",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]


class FarmerProfileViewSet(viewsets.ModelViewSet):
    queryset = FarmerProfile.objects.all()
    serializer_class = FarmerProfileSerializer


class PartnerProfileViewSet(viewsets.ModelViewSet):
    queryset = PartnerProfile.objects.all()
    serializer_class = PartnerProfileSerializer

    @action(detail=False, methods=['GET'], url_path='delivery-partners')
    def get_delivery_partners(self, request):
        try:
            verified_partners = self.queryset.filter(is_verified=True).filter(available_for_delivery=True)
            serializer = self.get_serializer(verified_partners, many=True)
            return Response(
                {
                    "message": "Verified partners retrieved successfully",
                    "status": "SUCCESS",
                    "data": serializer.data,
                }
            )
        except Exception as e:
            return Response(
                {
                    "message": "Failed to retrieve verified partners",
                    "status": "FAILURE",
                    "data": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
