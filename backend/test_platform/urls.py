"""
URL configuration for test_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from mock_server.views import ServeMockAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('testcases/', include('testcases.urls')),
    path('api/testcases/', include('testcases.urls')),
    path('api/testplans/', include('testcases.urls')),
    path('api-test/', include('api_test.urls')),
    path('api/user/', include('user_management.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/comments/', include('comments.urls')),  # 新增评论系统API
    path('api/environments/', include('environments.urls')),  # 新增环境管理API
    path('', include('mock_server.urls')),
    # Mock Server核心服务 - 必须放在最后，因为它会捕获所有/mock/路径
    re_path(r'^mock/(?P<full_path>.*)$', ServeMockAPIView.as_view(), name='serve_mock_api'),
]
