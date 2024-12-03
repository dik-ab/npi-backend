from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from announcements.models import Announcement

class AnnouncementListViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.url = reverse('announcement-list')

        # Create some announcements
        for i in range(15):
            Announcement.objects.create(title=f'Announcement {i}', content='Content', created_by=self.user)

    def test_get_announcements_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 10)  # Default per_page is 10
        self.assertEqual(response.data['pagination']['total_items'], 15)

    def test_get_announcements_unauthenticated(self):
        self.client.credentials()  # Remove authentication
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pagination(self):
        response = self.client.get(self.url, {'current_page': 2, 'per_page': 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 5)
        self.assertEqual(response.data['pagination']['current_page'], '2')
        self.assertEqual(response.data['pagination']['per_page'], '5')
        self.assertEqual(response.data['pagination']['total_pages'], 3)

    def test_invalid_pagination_params(self):
        response = self.client.get(self.url, {'current_page': 'invalid', 'per_page': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 10)  # Default per_page is 10

    def test_no_announcements(self):
        Announcement.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 0)
        self.assertEqual(response.data['pagination']['total_items'], 0)