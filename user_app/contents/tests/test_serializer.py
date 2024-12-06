from django.test import TestCase
from shared.models import Space, Project
from user_app.contents.models import Contents
from user_app.contents.serializer import ContentsSerializer
from django.utils import timezone


class ContentsSerializerTest(TestCase):
    def setUp(self):
        self.space = Space.objects.create(name="Test Space", description="Test Description")
        self.project = Project.objects.create(
            name="Test Project",
            description="Test Description",
            space=self.space,
        )
        self.contents_data = {
            'name': 'Test Content',
            'description': 'This is a test content description.',
            'project': self.project.id,
            'script_path': '/path/to/script',
            'is_10_return_move_on_display': True,
        }

    def test_valid_contents_serializer(self):
        """
        正常系
        """
        serializer = ContentsSerializer(data=self.contents_data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_contents_serializer_due_to_long_name(self):
        """
        異常系(名前上限不正)
        """
        self.contents_data['name'] = 'a' * 101
        serializer = ContentsSerializer(data=self.contents_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_invalid_contents_serializer_due_to_long_description(self):
        """
        異常系(説明上限不正)
        """
        self.contents_data['description'] = 'a' * 1001
        serializer = ContentsSerializer(data=self.contents_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('description', serializer.errors)

    def test_invalid_contents_serializer_due_to_nonexistent_project(self):
        """
        異常系(プロジェクト存在チェック不正)
        """
        self.contents_data['project'] = 9999
        serializer = ContentsSerializer(data=self.contents_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('project', serializer.errors)

    def test_duplicate_content_name_within_same_project(self):
        """
        異常系(名前重複チェック不正)
        """
        Contents.objects.create(
            name='Test Content',
            description='This is a test content description.',
            project=self.project,
            script_path='/path/to/script',
            is_10_return_move_on_display=True,
            last_updated_at=timezone.now()
        )
        serializer = ContentsSerializer(data=self.contents_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_to_representation(self):
        """
        正常系(取得時にカスタムフィールド追加)
        """
        content = Contents.objects.create(
            name='Test Content',
            description='This is a test content description.',
            project=self.project,
            script_path='/path/to/script',
            is_10_return_move_on_display=True,
            last_updated_at=timezone.now()
        )
        serializer = ContentsSerializer(content)
        data = serializer.data
        self.assertEqual(data['production_status'], 'UNDER_CONSTRUCTION')
