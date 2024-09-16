from django.urls import include, path
from rest_framework import routers
from notification.views import NotificationViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'notification', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]
