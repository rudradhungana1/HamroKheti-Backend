from django.urls import include, path
from rest_framework import routers

from users.views import UserViewSet, UserProfileViewSet, FarmerProfileViewSet, PartnerProfileViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'user', UserViewSet)
router.register(r'user-profile', UserProfileViewSet)
router.register(r'farmer-profile', FarmerProfileViewSet)
router.register(r'partner-profile', PartnerProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
