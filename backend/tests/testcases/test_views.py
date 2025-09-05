from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from user_management.models import User
from testcases.models import TestCase

class TestCaseViewSetTests(APITestCase):
    """
    Test suite for the TestCaseViewSet.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        # 清理现有数据，确保测试隔离
        TestCase.objects.all().delete()
        User.objects.all().delete()
        
        # Create users
        self.user = User.objects.create_user(username='testuser2025', password='password123')
        self.admin_user = User.objects.create_superuser(username='adminuser2025', password='password123', email='admin@example.com')

        # Create a TestCase instance for use in detail/update/delete tests
        self.test_case = TestCase.objects.create(
            title='Test Case 2025',
            description='A simple test case for 2025',
            priority='P1',
            status='blocked',  # Corrected: Use a valid choice
            assignee=self.admin_user
        )

        # URLs
        self.list_create_url = reverse('testcase-list')
        self.detail_url = reverse('testcase-detail', kwargs={'pk': self.test_case.pk})

    def test_list_testcases_unauthenticated(self):
        """
        Ensure unauthenticated users are forbidden from listing test cases.
        """
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_testcases_authenticated_user(self):
        """
        Ensure authenticated non-admin users can list test cases.
        """
        # 清理当前数据
        TestCase.objects.all().delete()
        
        # 重新创建测试用例
        test_case = TestCase.objects.create(
            title='Test Case 2025',
            description='A simple test case for 2025',
            priority='P1',
            status='blocked',
            assignee=self.admin_user
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 修复：检查分页结果中的results字段
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)
        else:
            self.assertEqual(len(response.data), 1)

    def test_retrieve_testcase_authenticated_user(self):
        """
        Ensure authenticated non-admin users can retrieve a test case.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.test_case.title)

    def test_create_testcase_as_user_forbidden(self):
        """
        Ensure non-admin users are forbidden from creating test cases.
        """
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'New Test Case',
            'priority': 'P2',
            'status': 'blocked',
        }
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_testcase_as_admin_success(self):
        """
        Ensure admin users can create a test case.
        """
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'title': 'Admin Created Case',
            'description': 'Successfully created by admin',
            'priority': 'P0',
            'status': 'passed',
            'assignee': self.admin_user.id
        }
        response = self.client.post(self.list_create_url, data, format='json')
        if response.status_code != status.HTTP_201_CREATED:
            print("Validation Error:", response.data)  # Print validation error
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TestCase.objects.count(), 2)
        self.assertEqual(response.data['title'], 'Admin Created Case')
        self.assertEqual(response.data['assignee'], self.admin_user.id)

    def test_update_testcase_as_user_forbidden(self):
        """
        Ensure non-admin users are forbidden from updating test cases.
        """
        self.client.force_authenticate(user=self.user)
        data = {'title': 'User Updated Title'}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_testcase_as_admin_success(self):
        """
        Ensure admin users can update a test case.
        """
        self.client.force_authenticate(user=self.admin_user)
        data = {'title': 'Admin Updated Title', 'priority': 'P0'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_case.refresh_from_db()
        self.assertEqual(self.test_case.title, 'Admin Updated Title')
        self.assertEqual(self.test_case.priority, 'P0')

    def test_delete_testcase_as_user_forbidden(self):
        """
        Ensure non-admin users are forbidden from deleting test cases.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_testcase_as_admin_success(self):
        """
        Ensure admin users can delete a test case.
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TestCase.objects.filter(pk=self.test_case.pk).exists())