from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ApiDefinitionViewSet, ApiTestCaseViewSet, ApiTestResultViewSet, api_test_debug_log

router = DefaultRouter()
# 修复：使用RESTful风格的路由命名
router.register(r'api-definitions', ApiDefinitionViewSet, basename='api-definition')
router.register(r'api-test-cases', ApiTestCaseViewSet, basename='api-test-case')
router.register(r'api-test-results', ApiTestResultViewSet, basename='api-test-result')

urlpatterns = [
    path('', include(router.urls)),
    path('debug-log/', api_test_debug_log, name='api_test_debug_log'),
]