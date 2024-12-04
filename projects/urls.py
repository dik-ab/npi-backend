from django.urls import path
from .views import ProjectListCreateAPIView, ProjectRetrieveUpdateDestroyAPIView

urlpatterns = [
    path("", ProjectListCreateAPIView.as_view(), name="project-list-create"),
    path('<int:project_id>/', ProjectRetrieveUpdateDestroyAPIView.as_view(), name='project-detail'),
]
