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
        # Create users
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.admin_user = User.objects.create_superuser(username='adminuser', password='password123', email='admin@example.com')

        # Create a TestCase instance for use in detail/update/delete tests
        self.test_case = TestCase.objects.create(
            title='Test Case 1',
            description='A simple test case',
            priority='P1',
            status='blocked',  # Use a valid choice
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
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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
            'status': 'blocked',  # Use valid status choice
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
            'status': 'blocked',  # Use valid status choice
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

class TestPlanViewSetTests(APITestCase):
    """
    Test suite for the TestPlanViewSet.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        # Create users
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.admin_user = User.objects.create_superuser(username='adminuser', password='password123', email='admin@example.com')

        # Create test cases
        self.test_case1 = TestCase.objects.create(
            title='Test Case 1',
            description='First test case',
            priority='P1',
            status='blocked',
            assignee=self.admin_user
        )
        self.test_case2 = TestCase.objects.create(
            title='Test Case 2',
            description='Second test case',
            priority='P2',
            status='blocked',
            assignee=self.admin_user
        )

        # Create a TestPlan instance
        self.test_plan = TestPlan.objects.create(
            name='Test Plan 1',
            assignee=self.admin_user,
            status='pending'
        )
        self.test_plan.test_cases.add(self.test_case1, self.test_case2)

        # URLs
        self.list_create_url = reverse('testplan-list')
        self.detail_url = reverse('testplan-detail', kwargs={'pk': self.test_plan.pk})

    def test_list_testplans_unauthenticated(self):
        """
        Ensure unauthenticated users are forbidden from listing test plans.
        """
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_testplans_authenticated_user(self):
        """
        Ensure authenticated non-admin users can list test plans.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_testplan_authenticated_user(self):
        """
        Ensure authenticated non-admin users can retrieve a test plan.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.test_plan.name)

    def test_create_testplan_as_user_forbidden(self):
        """
        Ensure non-admin users are forbidden from creating test plans.
        """
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'New Test Plan',
            'status': 'pending',
            'test_cases': [self.test_case1.id]
        }
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_testplan_as_admin_success(self):
        """
        Ensure admin users can create a test plan.
        """
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'name': 'Admin Created Plan',
            'status': 'pending',
            'assignee': self.admin_user.id,
            'test_cases': [self.test_case1.id, self.test_case2.id]
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TestPlan.objects.count(), 2)
        self.assertEqual(response.data['name'], 'Admin Created Plan')

    def test_update_testplan_as_user_forbidden(self):
        """
        Ensure non-admin users are forbidden from updating test plans.
        """
        self.client.force_authenticate(user=self.user)
        data = {'name': 'User Updated Plan'}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_testplan_as_admin_success(self):
        """
        Ensure admin users can update a test plan.
        """
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'Admin Updated Plan', 'status': 'running'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_plan.refresh_from_db()
        self.assertEqual(self.test_plan.name, 'Admin Updated Plan')
        self.assertEqual(self.test_plan.status, 'running')

    def test_delete_testplan_as_user_forbidden(self):
        """
        Ensure non-admin users are forbidden from deleting test plans.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_testplan_as_admin_success(self):
        """
        Ensure admin users can delete a test plan.
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TestPlan.objects.filter(pk=self.test_plan.pk).exists())

class TestCaseModelTests(TestCase):
    """
    Test suite for the TestCase model.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_testcase_creation(self):
        """
        Test creating a test case.
        """
        test_case = TestCase.objects.create(
            title='Sample Test Case',
            description='This is a sample test case',
            precondition='User must be logged in',
            status='blocked',
            module='Authentication',
            priority='P1',
            tags='login,authentication',
            version='v1.0',
            requirement_link='REQ-001',
            assignee=self.user
        )
        
        self.assertEqual(test_case.title, 'Sample Test Case')
        self.assertEqual(test_case.status, 'blocked')
        self.assertEqual(test_case.priority, 'P1')
        self.assertEqual(test_case.assignee, self.user)
        self.assertEqual(str(test_case), 'Sample Test Case')

    def test_testcase_default_values(self):
        """
        Test default values for test case fields.
        """
        test_case = TestCase.objects.create(
            title='Default Test Case',
            assignee=self.user
        )
        
        self.assertEqual(test_case.status, 'blocked')
        self.assertEqual(test_case.priority, 'P1')
        self.assertEqual(test_case.version, 'v1.0')
        self.assertEqual(test_case.precondition, '')
        self.assertEqual(test_case.description, '')

    def test_testcase_hierarchy(self):
        """
        Test test case hierarchy with parent-child relationships.
        """
        parent_case = TestCase.objects.create(
            title='Parent Test Case',
            assignee=self.user
        )
        
        child_case = TestCase.objects.create(
            title='Child Test Case',
            parent=parent_case,
            assignee=self.user
        )
        
        self.assertEqual(child_case.parent, parent_case)
        self.assertIn(child_case, parent_case.children.all())

class TestPlanModelTests(TestCase):
    """
    Test suite for the TestPlan model.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.test_case1 = TestCase.objects.create(
            title='Test Case 1',
            assignee=self.user
        )
        self.test_case2 = TestCase.objects.create(
            title='Test Case 2',
            assignee=self.user
        )

    def test_testplan_creation(self):
        """
        Test creating a test plan.
        """
        test_plan = TestPlan.objects.create(
            name='Sample Test Plan',
            assignee=self.user,
            status='pending'
        )
        test_plan.test_cases.add(self.test_case1, self.test_case2)
        
        self.assertEqual(test_plan.name, 'Sample Test Plan')
        self.assertEqual(test_plan.status, 'pending')
        self.assertEqual(test_plan.assignee, self.user)
        self.assertEqual(test_plan.test_cases.count(), 2)
        self.assertEqual(str(test_plan), 'Sample Test Plan')

    def test_testplan_default_status(self):
        """
        Test default status for test plan.
        """
        test_plan = TestPlan.objects.create(
            name='Default Test Plan',
            assignee=self.user
        )
        
        self.assertEqual(test_plan.status, 'pending')

    def test_testplan_many_to_many_relationship(self):
        """
        Test many-to-many relationship between test plan and test cases.
        """
        test_plan = TestPlan.objects.create(
            name='Test Plan with Cases',
            assignee=self.user
        )
        test_plan.test_cases.add(self.test_case1)
        
        self.assertIn(self.test_case1, test_plan.test_cases.all())
        self.assertIn(test_plan, self.test_case1.plans.all())

    def test_testplan_time_fields(self):
        """
        Test time fields in test plan.
        """
        from django.utils import timezone
        import datetime
        
        start_time = timezone.now()
        end_time = start_time + datetime.timedelta(days=7)
        
        test_plan = TestPlan.objects.create(
            name='Scheduled Test Plan',
            assignee=self.user,
            start_time=start_time,
            end_time=end_time,
            status='running'
        )
        
        self.assertEqual(test_plan.start_time, start_time)
        self.assertEqual(test_plan.end_time, end_time)
        self.assertEqual(test_plan.status, 'running')