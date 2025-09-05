from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器
router = DefaultRouter()
router.register(r'mocks', views.MockAPIViewSet)
router.register(r'logs', views.MockAPIUsageLogViewSet)

# URL配置
urlpatterns = [
    path('api/mock-server/', include(router.urls)),
]