from rest_framework import serializers
from django.test import TestCase
from announcements.models import Announcement
from announcements.serializers import AnnouncementSerializer

class AnnouncementSerializerTest(TestCase):
    def setUp(self):
        self.announcement_attributes = {
            'title': 'Test Announcement',
            'content': 'This is a test announcement.',
            'created_at': '2023-10-01T12:00:00Z',
            'updated_at': '2023-10-01T12:00:00Z'
        }

        self.announcement = Announcement.objects.create(**self.announcement_attributes)
        self.serializer = AnnouncementSerializer(instance=self.announcement)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'title', 'content', 'created_at', 'updated_at']))

    def test_title_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['title'], self.announcement_attributes['title'])

    def test_content_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['content'], self.announcement_attributes['content'])

    def test_created_at_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['created_at'], self.announcement_attributes['created_at'])

    def test_updated_at_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['updated_at'], self.announcement_attributes['updated_at'])

    def test_invalid_data(self):
        invalid_data = {
            'title': '',
            'content': 'This is a test announcement with invalid title.',
            'created_at': '2023-10-01T12:00:00Z',
            'updated_at': '2023-10-01T12:00:00Z'
        }
        serializer = AnnouncementSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), set(['title']))