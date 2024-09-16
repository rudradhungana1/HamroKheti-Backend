from django.urls import path
from .views import LoginView, ValidateTokenView

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('validate', ValidateTokenView.as_view(), name='validate_token'),
]
