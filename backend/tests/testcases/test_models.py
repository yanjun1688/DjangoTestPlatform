from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from testcases.models import TestCase as TestCaseModel, TestPlan, TestDataFile
import tempfile
import os
import json
import csv

User = get_user_model()


class TestCaseModelTest(TestCase):
    """测试用例模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.testcase = TestCaseModel.objects.create(
            title='测试用例1',
            description='测试描述',
            precondition='前置条件',
            module='用户管理',
            priority='P0',
            tags='用户,登录',
            assignee=self.user
        )
    
    def test_testcase_creation(self):
        """测试用例创建"""
        self.assertEqual(self.testcase.title, '测试用例1')
        self.assertEqual(self.testcase.description, '测试描述')
        self.assertEqual(self.testcase.precondition, '前置条件')
        self.assertEqual(self.testcase.status, 'blocked')  # 默认状态
        self.assertEqual(self.testcase.priority, 'P0')
        self.assertEqual(self.testcase.assignee, self.user)
    
    def test_testcase_str_method(self):
        """测试用例字符串表示"""
        self.assertEqual(str(self.testcase), '测试用例1')
    
    def test_testcase_hierarchy(self):
        """测试用例层级关系"""
        # 创建子测试用例
        child_testcase = TestCaseModel.objects.create(
            title='子测试用例',
            parent=self.testcase
        )
        
        # 验证父子关系
        self.assertEqual(child_testcase.parent, self.testcase)
        self.assertIn(child_testcase, self.testcase.children.all())
    
    def test_testcase_status_choices(self):
        """测试用例状态选择"""
        # 测试通过状态
        self.testcase.status = 'passed'
        self.testcase.save()
        self.assertEqual(self.testcase.get_status_display(), '通过')
        
        # 测试失败状态
        self.testcase.status = 'failed'
        self.testcase.save()
        self.assertEqual(self.testcase.get_status_display(), '失败')
    
    def test_testcase_priority_choices(self):
        """测试用例优先级选择"""
        # 测试高优先级
        self.testcase.priority = 'P0'
        self.testcase.save()
        self.assertEqual(self.testcase.get_priority_display(), '高')
        
        # 测试中优先级
        self.testcase.priority = 'P1'
        self.testcase.save()
        self.assertEqual(self.testcase.get_priority_display(), '中')


class TestPlanModelTest(TestCase):
    """测试计划模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.testcase1 = TestCaseModel.objects.create(title='测试用例1')
        self.testcase2 = TestCaseModel.objects.create(title='测试用例2')
        self.testplan = TestPlan.objects.create(
            name='测试计划1',
            assignee=self.user,
            status='pending'
        )
        self.testplan.test_cases.add(self.testcase1, self.testcase2)
    
    def test_testplan_creation(self):
        """测试计划创建"""
        self.assertEqual(self.testplan.name, '测试计划1')
        self.assertEqual(self.testplan.assignee, self.user)
        self.assertEqual(self.testplan.status, 'pending')
        self.assertEqual(self.testplan.test_cases.count(), 2)
    
    def test_testplan_str_method(self):
        """测试计划字符串表示"""
        self.assertEqual(str(self.testplan), '测试计划1')
    
    def test_testplan_status_choices(self):
        """测试计划状态选择"""
        # 测试进行中状态
        self.testplan.status = 'running'
        self.testplan.save()
        self.assertEqual(self.testplan.get_status_display(), '进行中')
        
        # 测试已完成状态
        self.testplan.status = 'completed'
        self.testplan.save()
        self.assertEqual(self.testplan.get_status_display(), '已完成')
    
    def test_testplan_testcase_relationship(self):
        """测试计划与测试用例关系"""
        # 验证测试用例关联
        self.assertIn(self.testcase1, self.testplan.test_cases.all())
        self.assertIn(self.testcase2, self.testplan.test_cases.all())
        
        # 验证反向关系
        self.assertIn(self.testplan, self.testcase1.plans.all())
        self.assertIn(self.testplan, self.testcase2.plans.all())


class TestDataFileModelTest(TestCase):
    """测试数据文件模型测试"""
    
    def setUp(self):
        self.testcase = TestCaseModel.objects.create(title='数据驱动测试用例')
        
        # 创建临时CSV文件
        self.csv_content = "name,age,email\nJohn,25,john@example.com\nJane,30,jane@example.com"
        self.csv_file = SimpleUploadedFile(
            "test_data.csv",
            self.csv_content.encode('utf-8'),
            content_type="text/csv"
        )
        
        # 创建临时JSON文件
        self.json_data = [
            {"name": "Alice", "age": 28, "city": "New York"},
            {"name": "Bob", "age": 32, "city": "Los Angeles"}
        ]
        self.json_file = SimpleUploadedFile(
            "test_data.json",
            json.dumps(self.json_data).encode('utf-8'),
            content_type="application/json"
        )
    
    def test_csv_file_creation(self):
        """测试CSV数据文件创建"""
        data_file = TestDataFile.objects.create(
            name='CSV测试数据',
            test_case=self.testcase,
            file=self.csv_file,
            file_type='csv',
            description='CSV格式的测试数据'
        )
        
        self.assertEqual(data_file.name, 'CSV测试数据')
        self.assertEqual(data_file.test_case, self.testcase)
        self.assertEqual(data_file.file_type, 'csv')
        self.assertTrue(data_file.file.name.endswith('.csv'))
    
    def test_json_file_creation(self):
        """测试JSON数据文件创建"""
        data_file = TestDataFile.objects.create(
            name='JSON测试数据',
            test_case=self.testcase,
            file=self.json_file,
            file_type='json'
        )
        
        self.assertEqual(data_file.file_type, 'json')
        self.assertTrue(data_file.file.name.endswith('.json'))
    
    def test_csv_file_parsing(self):
        """测试CSV文件解析"""
        data_file = TestDataFile.objects.create(
            name='CSV测试数据',
            test_case=self.testcase,
            file=self.csv_file,
            file_type='csv'
        )
        
        parsed_data = data_file.parse_file()
        
        # 验证表头
        expected_headers = ['name', 'age', 'email']
        self.assertEqual(parsed_data['headers'], expected_headers)
        
        # 验证数据行
        self.assertEqual(len(parsed_data['rows']), 2)
        self.assertEqual(parsed_data['rows'][0], ['John', '25', 'john@example.com'])
        self.assertEqual(parsed_data['rows'][1], ['Jane', '30', 'jane@example.com'])
    
    def test_json_file_parsing(self):
        """测试JSON文件解析"""
        data_file = TestDataFile.objects.create(
            name='JSON测试数据',
            test_case=self.testcase,
            file=self.json_file,
            file_type='json'
        )
        
        parsed_data = data_file.parse_file()
        
        # 验证表头（JSON键按字母排序）
        expected_headers = ['age', 'city', 'name']
        self.assertEqual(parsed_data['headers'], expected_headers)
        
        # 验证数据行
        self.assertEqual(len(parsed_data['rows']), 2)
        # 第一行：Alice, 28, New York
        self.assertEqual(parsed_data['rows'][0], ['28', 'New York', 'Alice'])
        # 第二行：Bob, 32, Los Angeles
        self.assertEqual(parsed_data['rows'][1], ['32', 'Los Angeles', 'Bob'])
    
    def test_file_size_methods(self):
        """测试文件大小相关方法"""
        data_file = TestDataFile.objects.create(
            name='测试文件大小',
            test_case=self.testcase,
            file=self.csv_file,
            file_type='csv'
        )
        
        # 测试文件大小获取
        file_size = data_file.get_file_size()
        self.assertGreater(file_size, 0)
        
        # 测试文件大小显示
        size_display = data_file.get_file_size_display()
        self.assertIn('B', size_display)  # 应该包含字节单位
    
    def test_data_count_method(self):
        """测试数据行数统计"""
        data_file = TestDataFile.objects.create(
            name='行数统计测试',
            test_case=self.testcase,
            file=self.csv_file,
            file_type='csv'
        )
        
        count = data_file.get_data_count()
        self.assertEqual(count, 2)  # CSV文件有2行数据
    
    def test_preview_data_method(self):
        """测试预览数据功能"""
        data_file = TestDataFile.objects.create(
            name='预览测试',
            test_case=self.testcase,
            file=self.csv_file,
            file_type='csv'
        )
        
        preview = data_file.get_preview_data(max_rows=1)
        
        # 应该只返回1行数据
        self.assertEqual(len(preview['rows']), 1)
        self.assertEqual(preview['rows'][0], ['John', '25', 'john@example.com'])
    
    def test_file_validation(self):
        """测试文件验证"""
        data_file = TestDataFile.objects.create(
            name='验证测试',
            test_case=self.testcase,
            file=self.csv_file,
            file_type='csv'
        )
        
        errors = data_file.validate_file()
        # 有效的CSV文件应该没有错误
        self.assertEqual(len(errors), 0)
    
    def test_testdatafile_str_method(self):
        """测试数据文件字符串表示"""
        data_file = TestDataFile.objects.create(
            name='字符串测试',
            test_case=self.testcase,
            file=self.csv_file,
            file_type='csv'
        )
        
        expected = "字符串测试 (CSV)"
        self.assertEqual(str(data_file), expected)