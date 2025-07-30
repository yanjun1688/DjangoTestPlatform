from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TestCaseViewSet, TestPlanViewSet, TestDataFileViewSet

router = DefaultRouter()
router.register(r'testcases', TestCaseViewSet)
router.register(r'testplans', TestPlanViewSet)
router.register(r'datafiles', TestDataFileViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 