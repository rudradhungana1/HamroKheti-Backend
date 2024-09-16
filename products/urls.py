from django.urls import include, path
from rest_framework import routers

from products.views import ProductViewSet, CommentViewSet, ReviewViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'product', ProductViewSet)
router.register(r'comment', CommentViewSet)
router.register(r'reviews', ReviewViewSet, basename='reviews')

urlpatterns = [
    path('', include(router.urls)),
]
