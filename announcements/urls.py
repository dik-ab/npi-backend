from django.test import TestCase
from django.urls import path
from .views import AnnouncementListView

# Create your tests here.

urlpatterns = [
    path('announcements/', AnnouncementListView.as_view(), name='announcement-list'),
]
