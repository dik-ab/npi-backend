from django.test import TestCase
from announcements.models import Announcement
from announcements.serializers import AnnouncementSerializer
from datetime import datetime, timedelta
from django.utils.timezone import make_aware

class AnnouncementSerializerTest(TestCase):
    def setUp(self):
        self.valid_data = {
            "title": "Test Announcement",
            "content": "This is a test announcement.",
            "announcements_from_at": make_aware(datetime.now()),
            "announcements_to_at": make_aware(datetime.now() + timedelta(days=1)),
            "file_path": "path/to/file",
        }
        self.invalid_data = {
            "title": "",
            "content": "This is a test announcement with invalid title.",
            "announcements_from_at": make_aware(datetime.now()),
            "announcements_to_at": make_aware(datetime.now() + timedelta(days=1)),
            "file_path": "path/to/file",
        }

    def test_valid_data(self):
        serializer = AnnouncementSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["title"], self.valid_data["title"])
        self.assertEqual(serializer.validated_data["content"], self.valid_data["content"])
        self.assertEqual(serializer.validated_data["announcements_from_at"], self.valid_data["announcements_from_at"])
        self.assertEqual(serializer.validated_data["announcements_to_at"], self.valid_data["announcements_to_at"])
        self.assertEqual(serializer.validated_data["file_path"], self.valid_data["file_path"])

    def test_invalid_data(self):
        serializer = AnnouncementSerializer(data=self.invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)
