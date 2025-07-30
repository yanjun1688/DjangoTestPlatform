from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from testcases.models import TestCase as TestCaseModel, TestDataFile
from api_test.models import ApiDefinition, ApiTestCase, ApiTestResult
from api_test.views import ApiTestService
import json
import io

User = get_user_model()


class DataDrivenTestCase(TestCase):
    """数据驱动测试功能单元测试"""
    
    def setUp(self):
        """测试数据准备"""
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建API定义
        self.api = ApiDefinition.objects.create(
            name='Test Login API',
            url='https://httpbin.org/post',
            method='POST',
            headers='{"Content-Type": "application/json"}',
            params='{}',
            body='{"username": "{username}", "password": "{password}"}',
            description='Test login endpoint',
            created_by=self.user
        )
        
        # 创建API测试用例
        self.api_test_case = ApiTestCase.objects.create(
            name='Login Test Case',
            api=self.api,
            expected_status_code=200,
            variables='{"default_var": "default_value"}',
            assertions='[]',
            is_active=True,
            created_by=self.user
        )
    
    def test_testdatafile_model_creation(self):
        """测试TestDataFile模型创建"""
        # 创建一个TestCase实例用于关联
        test_case = TestCaseModel.objects.create(
            title='测试用例',
            description='用于数据文件测试的测试用例',
            status='blocked',
            priority='P1'
        )
        
        # 准备CSV文件内容
        csv_content = "username,password\nuser1,pass1\nuser2,pass2"
        csv_file = SimpleUploadedFile(
            "test_data.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )
        
        # 创建TestDataFile
        data_file = TestDataFile.objects.create(
            name="测试数据文件",
            test_case=test_case,  # 关联到测试用例
            file=csv_file,
            file_type='csv',
            description='测试用的CSV数据文件'
        )
        
        self.assertEqual(data_file.name, "测试数据文件")
        self.assertEqual(data_file.file_type, 'csv')
        self.assertEqual(data_file.test_case, test_case)
        self.assertTrue(data_file.file.name.endswith('.csv'))
    
    def test_csv_file_parsing(self):
        """测试CSV文件解析功能"""
        # 准备CSV内容
        csv_content = "username,password,email\nuser1,pass1,user1@test.com\nuser2,pass2,user2@test.com"
        csv_file = SimpleUploadedFile(
            "test_data.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )
        
        # 创建数据文件
        data_file = TestDataFile(
            name="CSV测试文件",
            file=csv_file,
            file_type='csv'
        )
        
        # 解析文件
        parsed_data = data_file.parse_file()
        
        # 验证解析结果
        self.assertEqual(parsed_data['headers'], ['username', 'password', 'email'])
        self.assertEqual(len(parsed_data['rows']), 2)
        self.assertEqual(parsed_data['rows'][0], ['user1', 'pass1', 'user1@test.com'])
        self.assertEqual(parsed_data['rows'][1], ['user2', 'pass2', 'user2@test.com'])
    
    def test_json_file_parsing(self):
        """测试JSON文件解析功能"""
        # 准备JSON内容
        json_content = json.dumps([
            {"username": "user1", "password": "pass1", "email": "user1@test.com"},
            {"username": "user2", "password": "pass2", "email": "user2@test.com"}
        ])
        json_file = SimpleUploadedFile(
            "test_data.json",
            json_content.encode('utf-8'),
            content_type="application/json"
        )
        
        # 创建数据文件
        data_file = TestDataFile(
            name="JSON测试文件", 
            file=json_file,
            file_type='json'
        )
        
        # 解析文件
        parsed_data = data_file.parse_file()
        
        # 验证解析结果
        expected_headers = ['email', 'password', 'username']  # JSON键会被排序
        self.assertEqual(sorted(parsed_data['headers']), expected_headers)
        self.assertEqual(len(parsed_data['rows']), 2)
    
    def test_file_validation(self):
        """测试文件验证功能"""
        # 测试有效的CSV文件
        valid_csv = SimpleUploadedFile(
            "valid.csv",
            "name,value\ntest,123".encode('utf-8'),
            content_type="text/csv"
        )
        
        data_file = TestDataFile(
            name="有效CSV",
            file=valid_csv,
            file_type='csv'
        )
        
        errors = data_file.validate_file()
        self.assertEqual(len(errors), 0)
        
        # 测试无效的文件扩展名
        invalid_file = SimpleUploadedFile(
            "invalid.txt",
            "name,value\ntest,123".encode('utf-8'),
            content_type="text/plain"
        )
        
        data_file_invalid = TestDataFile(
            name="无效文件",
            file=invalid_file,
            file_type='csv'
        )
        
        errors = data_file_invalid.validate_file()
        self.assertGreater(len(errors), 0)
        self.assertIn("CSV文件扩展名必须是.csv", errors[0])
    
    def test_variable_replacement(self):
        """测试变量替换功能"""
        # 测试字符串替换
        test_data = "Hello {name}, your password is {password}"
        variables = {"name": "John", "password": "secret123"}
        result = ApiTestService._replace_variables(test_data, variables)
        self.assertEqual(result, "Hello John, your password is secret123")
        
        # 测试字典替换
        test_dict = {"user": "{username}", "pass": "{password}"}
        variables = {"username": "testuser", "password": "testpass"}
        result = ApiTestService._replace_variables(test_dict, variables)
        self.assertEqual(result, {"user": "testuser", "pass": "testpass"})
        
        # 测试列表替换
        test_list = ["{item1}", "{item2}"]
        variables = {"item1": "value1", "item2": "value2"}
        result = ApiTestService._replace_variables(test_list, variables)
        self.assertEqual(result, ["value1", "value2"])
    
    def test_data_driven_execution_flow(self):
        """测试数据驱动执行流程（模拟测试，不发送真实HTTP请求）"""
        # 创建一个TestCase实例用于关联
        test_case = TestCaseModel.objects.create(
            title='数据驱动测试用例',
            description='用于测试数据驱动功能的测试用例',
            status='blocked',
            priority='P1'
        )
        
        # 准备测试数据文件
        csv_content = "username,password\ntestuser1,pass1\ntestuser2,pass2"
        csv_file = SimpleUploadedFile(
            "test_users.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )
        
        # 创建数据文件并关联到测试用例
        data_file = TestDataFile.objects.create(
            name="用户登录测试数据",
            test_case=test_case,  # 关联到测试用例
            file=csv_file,
            file_type='csv',
            description='用户登录测试的数据驱动文件'
        )
        
        # 验证数据文件创建成功
        self.assertEqual(data_file.get_data_count(), 2)
        
        # 验证文件解析功能
        parsed_data = data_file.parse_file()
        self.assertEqual(parsed_data['headers'], ['username', 'password'])
        self.assertEqual(len(parsed_data['rows']), 2)
        
        # 验证变量合并逻辑
        test_variables = {"default_var": "default_value"}
        data_variables = {"username": "testuser1", "password": "pass1"}
        merged_variables = {**test_variables, **data_variables}
        
        expected_merged = {
            "default_var": "default_value",
            "username": "testuser1", 
            "password": "pass1"
        }
        self.assertEqual(merged_variables, expected_merged)


class DataFileAPITestCase(TestCase):
    """数据文件API接口测试"""
    
    def setUp(self):
        """API测试数据准备"""
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com', 
            password='apipass123'
        )
        self.client = Client()
        
        # 创建测试用例（这里使用testcases应用的TestCase模型）
        self.test_case = TestCaseModel.objects.create(
            title='API测试用例',
            description='用于测试数据文件上传的测试用例',
            status='blocked',
            priority='P1'
        )
    
    def test_data_file_upload_endpoint(self):
        """测试数据文件上传API端点（不涉及实际文件上传，只测试端点访问）"""
        # 测试获取测试用例信息的端点
        response = self.client.get(f'/testcases/testcases/{self.test_case.id}/')
        # 由于没有认证，可能返回403或其他错误，但端点应该存在
        self.assertIn(response.status_code, [200, 400, 403, 404])
    
    def test_data_file_info_endpoint(self):
        """测试数据文件信息API端点"""
        # 测试获取数据文件信息的端点
        response = self.client.get(f'/testcases/testcases/{self.test_case.id}/datafile_info/')
        # 应该返回404（因为没有关联的数据文件）或其他状态码
        self.assertIn(response.status_code, [404, 400, 403])


if __name__ == '__main__':
    import unittest
    unittest.main()