"""
Mock响应数据
提供测试中使用的各种Mock响应数据
"""

# API响应Mock数据
API_RESPONSES = {
    # 测试用例列表响应
    'testcase_list': {
        'count': 5,
        'next': None,
        'previous': None,
        'results': [
            {
                'id': 1,
                'title': '测试用例1',
                'description': '测试用例描述',
                'priority': 'P1',
                'status': 'blocked',
                'assignee': 1,
                'created_at': '2024-01-01T10:00:00Z',
                'updated_at': '2024-01-01T10:00:00Z'
            },
            {
                'id': 2,
                'title': '测试用例2',
                'description': '测试用例描述',
                'priority': 'P2',
                'status': 'passed',
                'assignee': 1,
                'created_at': '2024-01-01T11:00:00Z',
                'updated_at': '2024-01-01T11:00:00Z'
            }
        ]
    },
    
    # 测试用例详情响应
    'testcase_detail': {
        'id': 1,
        'title': '测试用例1',
        'description': '详细的测试用例描述',
        'priority': 'P1',
        'status': 'blocked',
        'assignee': 1,
        'created_at': '2024-01-01T10:00:00Z',
        'updated_at': '2024-01-01T10:00:00Z'
    },
    
    # 创建测试用例响应
    'testcase_create': {
        'id': 6,
        'title': '新建测试用例',
        'description': '新建的测试用例',
        'priority': 'P1',
        'status': 'blocked',
        'assignee': None,
        'created_at': '2024-01-01T15:00:00Z',
        'updated_at': '2024-01-01T15:00:00Z'
    }
}

# 错误响应Mock数据
ERROR_RESPONSES = {
    # 400 验证错误
    'validation_error': {
        'title': ['This field may not be blank.'],
        'priority': ['Invalid choice.']
    },
    
    # 404 不存在
    'not_found': {
        'detail': 'Not found.'
    },
    
    # 403 权限不足
    'permission_denied': {
        'detail': 'You do not have permission to perform this action.'
    }
}

# 用户数据Mock
USER_DATA = {
    'normal_user': {
        'id': 1,
        'username': 'testuser',
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'is_staff': False,
        'is_superuser': False
    },
    
    'admin_user': {
        'id': 2,
        'username': 'admin',
        'email': 'admin@example.com',
        'first_name': 'Admin',
        'last_name': 'User',
        'is_staff': True,
        'is_superuser': True
    }
}

# 测试状态数据
TEST_STATUSES = ['blocked', 'passed', 'failed', 'skipped']

# 测试优先级数据
TEST_PRIORITIES = ['P0', 'P1', 'P2', 'P3']

# 批量测试数据生成器
def generate_test_cases(count=10, status='blocked', priority='P1', assignee_id=1):
    """
    生成批量测试用例数据
    
    Args:
        count: 生成数量
        status: 默认状态
        priority: 默认优先级
        assignee_id: 默认分配人ID
    
    Returns:
        list: 测试用例数据列表
    """
    test_cases = []
    for i in range(count):
        test_case = {
            'id': 100 + i,
            'title': f'批量测试用例 {i+1}',
            'description': f'这是第 {i+1} 个批量生成的测试用例',
            'priority': priority,
            'status': status,
            'assignee': assignee_id,
            'created_at': f'2024-01-01T{10+i:02d}:00:00Z',
            'updated_at': f'2024-01-01T{10+i:02d}:00:00Z'
        }
        test_cases.append(test_case)
    
    return test_cases

# 性能测试数据
PERFORMANCE_TEST_DATA = {
    'large_dataset': generate_test_cases(1000),
    'medium_dataset': generate_test_cases(100),
    'small_dataset': generate_test_cases(10)
}

# 集成测试场景数据
INTEGRATION_SCENARIOS = {
    'user_workflow': {
        'users': [USER_DATA['normal_user'], USER_DATA['admin_user']],
        'test_cases': generate_test_cases(5),
        'expected_flow': [
            'create_test_case',
            'assign_test_case',
            'execute_test_case',
            'update_result',
            'generate_report'
        ]
    },
    
    'collaboration_scenario': {
        'users': [
            {'id': i, 'username': f'user_{i}', 'role': 'tester'} 
            for i in range(1, 4)
        ],
        'test_cases': generate_test_cases(15),
        'workflow': 'parallel_execution'
    }
}