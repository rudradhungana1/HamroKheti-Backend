from django.urls import include, path

from dashboard import views

urlpatterns = [
    path(r'counts', views.dashboard, name='dashboard'),
]
