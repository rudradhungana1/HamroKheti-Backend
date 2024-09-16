from django.urls import include, path
from rest_framework import routers

from news.views import NewsViewSet, VegetableMarketViewSet
from users.views import UserViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'news', NewsViewSet, basename='news')
router.register(r'vegetable-market', VegetableMarketViewSet, basename='vegetable-market')

urlpatterns = [
    path('', include(router.urls)),
]
