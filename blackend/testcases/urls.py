from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TestCaseViewSet, TestPlanViewSet

router = DefaultRouter()
router.register(r'testcases', TestCaseViewSet)
router.register(r'testplans', TestPlanViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 