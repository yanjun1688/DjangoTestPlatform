from django.db import models
from django.contrib.auth.models import User
from mptt.models import MPTTModel, TreeForeignKey
import reversion

@reversion.register()
class TestCase(MPTTModel):
    title = models.CharField(max_length=200, unique=True)
    precondition = models.TextField(blank=True)
    description = models.TextField(blank=True)
    STATUS_CHOICES = [
        ('passed', '通过'),
        ('failed', '失败'),
        ('blocked', '阻塞'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='blocked')
    module = models.CharField(max_length=100, blank=True)
    PRIORITY_CHOICES = [
        ('P0', '高'),
        ('P1', '中'),
        ('P2', '低'),
    ]
    priority = models.CharField(max_length=2, choices=PRIORITY_CHOICES, default='P1')
    tags = models.CharField(max_length=200, blank=True)
    version = models.CharField(max_length=20, default='v1.0')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    requirement_link = models.CharField(max_length=200, blank=True, help_text='需求ID或外部链接')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='testcases')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class MPTTMeta:
        order_insertion_by = ['title']

    def __str__(self):
        return self.title

class TestPlan(models.Model):
    name = models.CharField(max_length=200)
    test_cases = models.ManyToManyField(TestCase, related_name='plans', blank=True)
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='testplans')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    STATUS_CHOICES = [
        ('pending', '待执行'),
        ('running', '进行中'),
        ('completed', '已完成'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
