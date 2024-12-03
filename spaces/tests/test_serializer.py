from django.test import TestCase
from spaces.serializer import SpaceSerializer, SpaceAccountCreateSerializer, SpaceAccountSerializer, PermissionSerializer, SpaceAccountPermissionCreateSerializer, SpaceAccountPermissionSerializer
from spaces.models import Space, SpaceAccount, Permission, SpaceAccountPermission
from accounts.models import Account


class SpaceSerializerTest(TestCase):
    def setUp(self):
        self.valid_data = {
            "name": "Test Space",
            "icon_image_path": "path/to/icon.png",
            "description": "This is a test space description.",
        }
        self.invalid_data = {
            "name": "",
            "icon_image_path": "a" * 501,
            "description": "a" * 1001,
        }

    def test_valid_data(self):
        serializer = SpaceSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["name"], self.valid_data["name"])
        self.assertEqual(serializer.validated_data["icon_image_path"], self.valid_data["icon_image_path"])
        self.assertEqual(serializer.validated_data["description"], self.valid_data["description"])

    def test_invalid_data(self):
        serializer = SpaceSerializer(data=self.invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)
        self.assertIn("icon_image_path", serializer.errors)
        self.assertIn("description", serializer.errors)


class PermissionSerializerTest(TestCase):
    def setUp(self):
        self.valid_data = {
            "name": "スペース管理者",
        }
        self.invalid_data = {
            "name": "",
        }

    def test_valid_data(self):
        serializer = PermissionSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["name"], self.valid_data["name"])

    def test_invalid_data(self):
        serializer = PermissionSerializer(data=self.invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)


class SpaceAccountCreateSerializerTest(TestCase):
    def setUp(self):
        self.space = Space.objects.create(name="Test Space", icon_image_path="path/to/icon.png", description="This is a test space description.")
        self.account = Account.objects.create(name="testuser", email="testuser@example.com")
        self.valid_data = {
            "space": self.space.id,
            "account": self.account.id,
        }
        self.invalid_data = {
            "space": 999,
            "account": 999,
        }

    def test_valid_data(self):
        """
        正常時系
        """
        serializer = SpaceAccountCreateSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["space"], self.valid_data["space"])
        self.assertEqual(serializer.validated_data["account"], self.valid_data["account"])

    def test_invalid_data(self):
        """
        異常系(型エラー)
        """
        serializer = SpaceAccountCreateSerializer(data=self.invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("space", serializer.errors)
        self.assertIn("account", serializer.errors)

    def test_duplicate_data(self):
        """
        異常系(重複)
        """
        SpaceAccount.objects.create(space=self.space, account=self.account)
        serializer = SpaceAccountCreateSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)


class SpaceAccountSerializerTest(TestCase):
    def setUp(self):
        self.space = Space.objects.create(name="Test Space", icon_image_path="path/to/icon.png", description="This is a test space description.")
        self.account = Account.objects.create(name="testuser", email="testuser@example.com")
        self.space_account = SpaceAccount.objects.create(space=self.space, account=self.account)

    def test_space_account_serializer(self):
        """
        想定データの取得
        """
        serializer = SpaceAccountSerializer(self.space_account)
        self.assertEqual(serializer.data["id"], self.space_account.id)
        self.assertEqual(serializer.data["space"]["id"], self.space.id)
        self.assertEqual(serializer.data["space"]["name"], self.space.name)
        self.assertEqual(serializer.data["space"]["icon_image_path"], self.space.icon_image_path)
        self.assertEqual(serializer.data["space"]["description"], self.space.description)
        self.assertEqual(serializer.data["account"]["id"], self.account.id)
        self.assertEqual(serializer.data["account"]["name"], self.account.name)
        self.assertEqual(serializer.data["account"]["email"], self.account.email)


class SpaceAccountCreatePermissionSerializerTest(TestCase):
    def setUp(self):
        self.space = Space.objects.create(name="Test Space", icon_image_path="path/to/icon.png", description="This is a test space description.")
        self.account = Account.objects.create(name="testuser", email="testuser@example.com")
        self.space_account = SpaceAccount.objects.create(space=self.space, account=self.account)
        self.permission = Permission.objects.create(name="スペース管理者")
        self.valid_data = {
            "space_account": self.space_account.id,
            "permission": self.permission.id,
        }
        self.invalid_data = {
            "space_account": 999,
            "permission": 999,
        }

    def test_valid_data(self):
        """
        正常時系
        """
        serializer = SpaceAccountPermissionCreateSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["space_account"], self.valid_data["space_account"])
        self.assertEqual(serializer.validated_data["permission"], self.valid_data["permission"])

    def test_invalid_data(self):
        """
        異常系(型エラー)
        """
        serializer = SpaceAccountPermissionCreateSerializer(data=self.invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("space_account", serializer.errors)
        self.assertIn("permission", serializer.errors)

    def test_duplicate_data(self):
        """
        異常系(重複)
        """
        SpaceAccountPermission.objects.create(space_account=self.space_account, permission=self.permission)
        serializer = SpaceAccountPermissionCreateSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)


class SpaceAccountPermissionSerializerTest(TestCase):
    def setUp(self):
        self.space = Space.objects.create(name="Test Space", icon_image_path="path/to/icon.png", description="This is a test space description.")
        self.account = Account.objects.create(name="testuser", email="testuser@example.com")
        self.space_account = SpaceAccount.objects.create(space=self.space, account=self.account)
        self.permission = Permission.objects.create(name="スペース管理者")
        self.space_account_permission = SpaceAccountPermission.objects.create(space_account=self.space_account, permission=self.permission)

    def test_space_account_permission_serializer(self):
        """
        想定データの取得
        """
        serializer = SpaceAccountPermissionSerializer(self.space_account_permission)
        self.assertEqual(serializer.data["id"], self.space_account_permission.id)
        self.assertEqual(serializer.data["space_account"]["id"], self.space_account.id)
        self.assertEqual(serializer.data["space_account"]["space"]["id"], self.space.id)
        self.assertEqual(serializer.data["space_account"]["space"]["name"], self.space.name)
        self.assertEqual(serializer.data["space_account"]["space"]["icon_image_path"], self.space.icon_image_path)
        self.assertEqual(serializer.data["space_account"]["space"]["description"], self.space.description)
        self.assertEqual(serializer.data["space_account"]["account"]["id"], self.account.id)
        self.assertEqual(serializer.data["space_account"]["account"]["name"], self.account.name)
        self.assertEqual(serializer.data["space_account"]["account"]["email"], self.account.email)
        self.assertEqual(serializer.data["permission"]["id"], self.permission.id)
        self.assertEqual(serializer.data["permission"]["name"], self.permission.name)
