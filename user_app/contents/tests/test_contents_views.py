from django_hosts.resolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from shared.models import Account, Space, SpaceAccount, Permission, SpaceAccountPermission, Project
from user_app.contents.models import Contents
from django.utils import timezone
from django.contrib.auth.hashers import make_password


class ContentsListCreateAPIViewTests(APITestCase):
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
        self.permission1 = Permission.objects.create(name='creator')

        # 検証用スペースアカウント権限の作成
        self.space_account_permission1 = SpaceAccountPermission.objects.create(
            space_account=self.space_account1,
            permission=Permission.objects.get(name='creator')
        )

        # 検証用プロジェクトの作成
        self.project1 = Project.objects.create(
            name="Test Project",
            description="Test Description",
            space=self.space1,
        )
        self.project_id = self.project1.id

        # JWTトークンの取得
        login_response = self.client.post(
            self.login_url, {"email": "test@example.com", "password": "securepassword1"}
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.client.cookies["access_token"] = login_response.cookies.get(
            "access_token"
        ).value

    def test_get_contents_list(self):
        """
        正常系(一覧取得)
        """
        production_status_id = 1
        Contents.objects.create(
            name='Test Content1',
            description='This is a test content description.',
            project=self.project1,
            script_path='/path/to/script',
            is_10_return_move_on_display=True,
            last_updated_at=timezone.now(),
            production_status_id=production_status_id
        )
        Contents.objects.create(
            name='Test Content2',
            description='This is a test content description.',
            project=self.project1,
            script_path='/path/to/script',
            is_10_return_move_on_display=True,
            last_updated_at=timezone.now(),
            production_status_id=2
        )

        url = reverse('contents-list-create', kwargs={'space_id': self.space_id, 'project_id': self.project_id}, host='user_app')
        response = self.client.get(url, {'page': 1, 'per_page': 10})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)

    def test_get_contents_list_with_production_status(self):
        """
        正常系(一覧取得): production_statusで絞り込み
        """
        production_status_id = 2
        Contents.objects.create(
            name='Test Content1',
            description='This is a test content description.',
            project=self.project1,
            script_path='/path/to/script',
            is_10_return_move_on_display=True,
            last_updated_at=timezone.now(),
            production_status_id=production_status_id
        )
        Contents.objects.create(
            name='Test Content2',
            description='This is a test content description.',
            project=self.project1,
            script_path='/path/to/script',
            is_10_return_move_on_display=True,
            last_updated_at=timezone.now(),
        )

        url = reverse('contents-list-create', kwargs={'space_id': self.space_id, 'project_id': self.project_id}, host='user_app')
        response = self.client.get(url, {'page': 1, 'per_page': 10, 'production_status': production_status_id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['production_status'], 'COMPLETION')

    def test_create_contents(self):
        """
        正常系(新規作成)
        """
        url = reverse('contents-list-create', kwargs={'space_id': self.space_id, 'project_id': self.project_id}, host='user_app')
        data = {
            'name': 'New Contents',
            'description': 'Contents description'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Contents.objects.count(), 1)
        self.assertEqual(Contents.objects.get().name, 'New Contents')

    def test_get_contents_list_without_permission(self):
        """
        異常系(権限なし)(一覧取得)
        """
        self.client.force_authenticate(user=None)
        url = reverse('contents-list-create', kwargs={'space_id': self.space_id, 'project_id': self.project_id}, host='user_app')
        response = self.client.get(url, {'page': 1, 'per_page': 10})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_contents_without_permission(self):
        """
        異常系(権限なし)(新規作成)
        """
        self.client.force_authenticate(user=None)
        url = reverse('contents-list-create', kwargs={'space_id': self.space_id, 'project_id': self.project_id}, host='user_app')
        data = {
            'name': 'New Contents',
            'description': 'Contents description'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Contents.objects.count(), 0)

    def test_get_contents_list_without_space_permission(self):
        """
        異常系(スペースでの操作権限なし)(一覧取得)
        """
        self.space_account_permission1.delete()

        url = reverse('contents-list-create', kwargs={'space_id': self.space_id, 'project_id': self.project_id}, host='user_app')
        response = self.client.get(url, {'page': 1, 'per_page': 10})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_contents_without_space_permission(self):
        """
        異常系(スペースでの操作権限なし)(新規作成)
        """
        self.space_account_permission1.delete()

        url = reverse('contents-list-create', kwargs={'space_id': self.space_id, 'project_id': self.project_id}, host='user_app')
        data = {
            'name': 'New Contents',
            'description': 'Contents description'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Contents.objects.count(), 0)


class ContentsRetrieveReproduceUpdateDestroyAPIViewTests(APITestCase):
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
        self.permission1 = Permission.objects.create(name='creator')

        # 検証用スペースアカウント権限の作成
        self.space_account_permission1 = SpaceAccountPermission.objects.create(
            space_account=self.space_account1,
            permission=Permission.objects.get(name='creator')
        )

        # 検証用プロジェクトの作成
        self.project1 = Project.objects.create(
            name="Test Project",
            description="Test Description",
            space=self.space1,
        )
        self.project_id = self.project1.id

        # 検証用コンテンツの作成
        self.contents1 = Contents.objects.create(
            name='Test Content1',
            description='This is a test content description.',
            project=self.project1,
            script_path='/path/to/script',
            is_10_return_move_on_display=True,
            last_updated_at=timezone.now(),
            production_status_id=1
        )
        self.contents_id = self.contents1.id

        # JWTトークンの取得
        login_response = self.client.post(
            self.login_url, {"email": "test@example.com", "password": "securepassword1"}
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.client.cookies["access_token"] = login_response.cookies.get(
            "access_token"
        ).value

    def test_get_contents_detail(self):
        """
        正常系(詳細取得)
        """
        url = reverse('contents-detail', kwargs={'space_id': self.space_id, 'project_id': self.project_id, 'contents_id': self.contents_id}, host='user_app')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], 'Test Content1')
        print(response.data)

    def test_get_contents_detail_without_permission(self):
        """
        異常系(権限なし)(詳細取得)
        """
        self.client.force_authenticate(user=None)
        url = reverse('contents-detail', kwargs={'space_id': self.space_id, 'project_id': self.project_id, 'contents_id': self.contents_id}, host='user_app')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_contents_detail_without_space_permission(self):
        """
        異常系(スペースでの操作権限なし)(詳細取得)
        """
        self.space_account_permission1.delete()

        url = reverse('contents-detail', kwargs={'space_id': self.space_id, 'project_id': self.project_id, 'contents_id': self.contents_id}, host='user_app')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reproduce_contents(self):
        """
        正常系(複製)
        """
        url = reverse('contents-detail', kwargs={'space_id': self.space_id, 'project_id': self.project_id, 'contents_id': self.contents_id}, host='user_app')
        data = {
            'name': 'Reproduced Content',
            'description': 'Reproduced description'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Contents.objects.count(), 2)
        self.assertEqual(Contents.objects.get(name='Reproduced Content').description, 'Reproduced description')

    def test_reproduce_contents_without_permission(self):
        """
        異常系(権限なし)(複製)
        """
        self.client.force_authenticate(user=None)
        url = reverse('contents-detail', kwargs={'space_id': self.space_id, 'project_id': self.project_id, 'contents_id': self.contents_id}, host='user_app')
        data = {
            'name': 'Reproduced Content',
            'description': 'Reproduced description'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Contents.objects.count(), 1)

    def test_reproduce_contents_without_space_permission(self):
        """
        異常系(スペースでの操作権限なし)(複製)
        """
        self.space_account_permission1.delete()

        url = reverse('contents-detail', kwargs={'space_id': self.space_id, 'project_id': self.project_id, 'contents_id': self.contents_id}, host='user_app')
        data = {
            'name': 'Reproduced Content',
            'description': 'Reproduced description'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Contents.objects.count(), 1)

    def test_update_contents(self):
        """
        正常系(更新)
        """
        url = reverse('contents-detail', kwargs={'space_id': self.space_id, 'project_id': self.project_id, 'contents_id': self.contents_id}, host='user_app')
        data = {
            'name': 'Updated Content',
            'description': 'Updated description'
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Contents.objects.get(id=self.contents_id).name, 'Updated Content')

    def test_update_contents_without_permission(self):
        """
        異常系(権限なし)(更新)
        """
        self.client.force_authenticate(user=None)
        url = reverse('contents-detail', kwargs={'space_id': self.space_id, 'project_id': self.project_id, 'contents_id': self.contents_id}, host='user_app')
        data = {
            'name': 'Updated Content',
            'description': 'Updated description'
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_contents_without_space_permission(self):
        """
        異常系(スペースでの操作権限なし)(更新)
        """
        self.space_account_permission1.delete()

        url = reverse('contents-detail', kwargs={'space_id': self.space_id, 'project_id': self.project_id, 'contents_id': self.contents_id}, host='user_app')
        data = {
            'name': 'Updated Content',
            'description': 'Updated description'
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_contents(self):
        """
        正常系(削除)
        """
        url = reverse('contents-detail', kwargs={'space_id': self.space_id, 'project_id': self.project_id, 'contents_id': self.contents_id}, host='user_app')
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Contents.objects.filter(id=self.contents_id).count(), 0)

    def test_delete_contents_without_permission(self):
        """
        異常系(権限なし)(削除)(削除)
        """
        self.client.force_authenticate(user=None)
        url = reverse('contents-detail', kwargs={'space_id': self.space_id, 'project_id': self.project_id, 'contents_id': self.contents_id}, host='user_app')
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_contents_without_space_permission(self):
        """
        異常系(スペースでの操作権限なし)(削除)(削除)
        """
        self.space_account_permission1.delete()

        url = reverse('contents-detail', kwargs={'space_id': self.space_id, 'project_id': self.project_id, 'contents_id': self.contents_id}, host='user_app')
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
