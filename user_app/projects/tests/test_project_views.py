from django_hosts.resolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from shared.models import Account, Space, SpaceAccount, Permission, SpaceAccountPermission, Project
from django.utils import timezone
from django.contrib.auth.hashers import make_password


class ProjectListCreateAPIViewTests(APITestCase):
    def setUp(self):
        self.login_url = reverse("login", host='user_app')

        # 検証用アカウントの作成
        self.account1 = Account.objects.create(
            email="test@example.com",
            password=make_password("securepassword1"),
            name="Test User",
        )

        # 検証用スペースの作成
        self.space1 = Space.objects.create(name='Test Space 1', icon_image_path='path/to/icon1.png', description='This is a test space description.')
        self.space_id = self.space1.id

        # 検証用スペースアカウントの作成
        self.space_account1 = SpaceAccount.objects.create(space=self.space1, account=self.account1)

        # 検証用権限の作成
        self.permission1 = Permission.objects.create(name='space_admin')

        # 検証用スペースアカウント権限の作成
        self.space_account_permission1 = SpaceAccountPermission.objects.create(
            space_account=self.space_account1,
            permission=Permission.objects.get(name='space_admin')
        )

        # JWTトークンの取得
        login_response = self.client.post(
            self.login_url, {"email": "test@example.com", "password": "securepassword1"}
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.client.cookies["access_token"] = login_response.cookies.get(
            "access_token"
        ).value

    def test_get_project_list(self):
        """
        正常系
        """
        Project.objects.create(name='Project 1', space=self.space1, last_updated_at=timezone.now())
        Project.objects.create(name='Project 2', space=self.space1, last_updated_at=timezone.now())

        url = reverse('project-list-create', kwargs={'space_id': self.space_id}, host='user_app')
        response = self.client.get(url, {'page': 1, 'per_page': 10})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)

    def test_create_project(self):
        """
        正常系
        """
        url = reverse('project-list-create', kwargs={'space_id': self.space_id}, host='user_app')
        data = {
            'name': 'New Project',
            'description': 'Project description'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.get().name, 'New Project')

    def test_get_project_list_without_permission(self):
        """
        異常系(権限なし)
        """
        self.client.force_authenticate(user=None)
        url = reverse('project-list-create', kwargs={'space_id': self.space_id}, host='user_app')
        response = self.client.get(url, {'page': 1, 'per_page': 10})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_project_without_permission(self):
        """
        異常系(権限なし)
        """
        self.client.force_authenticate(user=None)
        url = reverse('project-list-create', kwargs={'space_id': self.space_id}, host='user_app')
        data = {
            'name': 'New Project',
            'description': 'Project description'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Project.objects.count(), 0)

    def test_get_project_list_without_space_permission(self):
        """
        異常系(スペースでの操作権限なし)
        """
        self.space_account_permission1.delete()

        url = reverse('project-list-create', kwargs={'space_id': self.space_id}, host='user_app')
        response = self.client.get(url, {'page': 1, 'per_page': 10})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_project_without_space_permission(self):
        """
        異常系(スペースでの操作権限なし)
        """
        self.space_account_permission1.delete()

        url = reverse('project-list-create', kwargs={'space_id': self.space_id}, host='user_app')
        data = {
            'name': 'New Project',
            'description': 'Project description'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Project.objects.count(), 0)


class ProjectRetrieveUpdateDestroyAPIViewTests(APITestCase):
    def setUp(self):
        self.login_url = reverse("login", host='user_app')

        # 検証用アカウントの作成
        self.account1 = Account.objects.create(
            email="test@example.com",
            password=make_password("securepassword1"),
            name="Test User",
        )

        # 検証用スペースの作成
        self.space1 = Space.objects.create(name='Test Space 1', icon_image_path='path/to/icon1.png', description='This is a test space description.')
        self.space_id = self.space1.id

        # 検証用スペースアカウントの作成
        self.space_account1 = SpaceAccount.objects.create(space=self.space1, account=self.account1)

        # 検証用権限の作成
        self.permission1 = Permission.objects.create(name='space_admin')

        # 検証用スペースアカウント権限の作成
        self.space_account_permission1 = SpaceAccountPermission.objects.create(
            space_account=self.space_account1,
            permission=Permission.objects.get(name='space_admin')
        )

        # 検証用プロジェクトの作成
        self.project1 = Project.objects.create(name='Project 1', space=self.space1, last_updated_at=timezone.now())
        self.project_id = self.project1.id

        # JWTトークンの取得
        login_response = self.client.post(
            self.login_url, {"email": "test@example.com", "password": "securepassword1"}
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.client.cookies["access_token"] = login_response.cookies.get(
            "access_token"
        ).value

    def test_get_project_detail(self):
        """
        正常系
        """
        url = reverse('project-detail', kwargs={'space_id': self.space_id, 'project_id': self.project_id}, host='user_app')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], 'Project 1')

    def test_update_project(self):
        """
        正常系
        """
        url = reverse('project-detail', kwargs={'space_id': self.space_id, 'project_id': self.project_id}, host='user_app')
        data = {
            'name': 'Updated Project',
            'description': 'Updated description'
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Project.objects.get(id=self.project_id).name, 'Updated Project')

    def test_delete_project(self):
        """
        正常系
        """
        url = reverse('project-detail', kwargs={'space_id': self.space_id, 'project_id': self.project_id}, host='user_app')
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Project.objects.filter(id=self.project_id).exists())

    def test_get_project_detail_without_permission(self):
        """
        異常系(権限なし)
        """
        self.client.force_authenticate(user=None)
        url = reverse('project-detail', kwargs={'space_id': self.space_id, 'project_id': self.project_id}, host='user_app')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_project_without_permission(self):
        """
        異常系(権限なし)
        """
        self.client.force_authenticate(user=None)
        url = reverse('project-detail', kwargs={'space_id': self.space_id, 'project_id': self.project_id}, host='user_app')
        data = {
            'name': 'Updated Project',
            'description': 'Updated description'
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Project.objects.get(id=self.project_id).name, 'Project 1')

    def test_delete_project_without_permission(self):
        """
        異常系(権限なし)
        """
        self.client.force_authenticate(user=None)
        url = reverse('project-detail', kwargs={'space_id': self.space_id, 'project_id': self.project_id}, host='user_app')
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Project.objects.filter(id=self.project_id).exists())

    def test_get_project_detail_without_space_permission(self):
        """
        異常系(スペースでの操作権限なし)
        """
        self.space_account_permission1.delete()

        url = reverse('project-detail', kwargs={'space_id': self.space_id, 'project_id': self.project_id}, host='user_app')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_project_without_space_permission(self):
        """
        異常系(スペースでの操作権限なし)
        """
        self.space_account_permission1.delete()

        url = reverse('project-detail', kwargs={'space_id': self.space_id, 'project_id': self.project_id}, host='user_app')
        data = {
            'name': 'Updated Project',
            'description': 'Updated description'
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Project.objects.get(id=self.project_id).name, 'Project 1')

    def test_delete_project_without_space_permission(self):
        """
        異常系(スペースでの操作権限なし)
        """
        self.space_account_permission1.delete()

        url = reverse('project-detail', kwargs={'space_id': self.space_id, 'project_id': self.project_id}, host='user_app')
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Project.objects.filter(id=self.project_id).exists())
