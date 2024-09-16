from django.urls import include, path
from rest_framework import routers

from orders.views import OrderViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'order', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]
