from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EnvironmentViewSet, EnvironmentVariableViewSet

router = DefaultRouter()
router.register(r'environments', EnvironmentViewSet, basename='environment')
router.register(r'variables', EnvironmentVariableViewSet, basename='environment-variable')

urlpatterns = [
    path('', include(router.urls)),
]