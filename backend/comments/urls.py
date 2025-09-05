from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    # 评论相关
    path('', views.CommentListCreateView.as_view(), name='comment-list-create'),
    path('<int:pk>/', views.CommentDetailView.as_view(), name='comment-detail'),
    path('create/', views.create_comment, name='comment-create'),
    
    # 通知相关
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('notifications/mark-read/', views.mark_notifications_as_read, name='mark-notifications-read'),
    path('notifications/summary/', views.notification_summary, name='notification-summary'),
    
    # 用户搜索（@提及功能）
    path('users/search/', views.search_users, name='user-search'),
]