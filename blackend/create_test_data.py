from user_management.models import User
from testcases.models import TestCase
from api_test.models import TestRun

# 创建测试用户
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'first_name': '测试',
        'last_name': '用户',
        'email': 'test@example.com',
        'is_active': True
    }
)
if created:
    user.set_password('testpass123')
    user.save()
    print(f"Created test user: {user.username}")
else:
    print(f"Test user already exists: {user.username}")

# 创建测试用例
testcase, created = TestCase.objects.get_or_create(
    title='测试评论功能的用例',
    defaults={
        'description': '这是一个用于测试评论功能的测试用例',
        'precondition': '需要用户登录',
        'status': 'blocked',
        'priority': 'P1'
    }
)
if created:
    print(f"Created test case: {testcase.title}")
else:
    print(f"Test case already exists: {testcase.title}")

# 创建测试执行记录
testrun, created = TestRun.objects.get_or_create(
    name='评论功能测试执行',
    defaults={
        'status': 'completed',
        'total_tests': 1,
        'passed_tests': 1,
        'failed_tests': 0,
        'error_tests': 0,
        'executed_by': user
    }
)
if created:
    print(f"Created test run: {testrun.name}")
else:
    print(f"Test run already exists: {testrun.name}")

print(f"TestCase ID: {testcase.id}")
print(f"TestRun ID: {testrun.id}")
print(f"User ID: {user.id}")