from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TestRunViewSet

router = DefaultRouter()
router.register(r'test-runs', TestRunViewSet)

urlpatterns = [
    path('', include(router.urls)),
]