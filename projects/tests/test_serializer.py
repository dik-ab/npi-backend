from django.test import TestCase
from projects.models import Project
from spaces.models import Space
from projects.serializer import ProjectSerializer
from django.utils import timezone


class ProjectSerializerTest(TestCase):
    def setUp(self):
        self.space = Space.objects.create(name="Test Space", description="Test Description")
        self.project_data = {
            'name': 'Test Project',
            'description': 'Test Description',
            'space': self.space.id,
        }
        self.project_data['last_updated_at'] = timezone.now()

    def test_valid_project_serializer(self):
        """
        正常系
        """
        serializer = ProjectSerializer(data=self.project_data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_project_name_too_long(self):
        """
        異常系(名前上限不正)
        """
        self.project_data['name'] = 'a' * 101
        serializer = ProjectSerializer(data=self.project_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_invalid_project_description_too_long(self):
        """
        異常系(説明上限不正)
        """
        self.project_data['description'] = 'a' * 1001
        serializer = ProjectSerializer(data=self.project_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('description', serializer.errors)

    def test_invalid_space_does_not_exist(self):
        """
        異常系(スペース存在チェック不正)
        """
        self.project_data['space'] = 9999
        serializer = ProjectSerializer(data=self.project_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('space', serializer.errors)

    def test_duplicate_project_name_and_space(self):
        """
        異常系(名前重複チェック不正)
        """
        Project.objects.create(
            name='Test Project',
            description='Test Description',
            space=self.space
        )
        serializer = ProjectSerializer(data=self.project_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_to_representation(self):
        """
        正常系(取得時にカスタムフィールド追加)
        """
        project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            space=self.space,
            last_updated_at=timezone.now()
        )
        serializer = ProjectSerializer(project)
        data = serializer.data
        self.assertEqual(data['last_status'], 'public')
        self.assertEqual(data['project_play_count_last_month'], 12345)
        self.assertEqual(data['projects_play_count_two_months_ago'], 67890)
