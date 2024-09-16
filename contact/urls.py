from django.urls import include, path
from rest_framework import routers

from contact.views import ContactViewSet
from orders.views import OrderViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'contact', ContactViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
