from django.urls import path
from django.urls import path, include
from user_app.projects.views import ProjectListCreateAPIView, ProjectRetrieveUpdateDestroyAPIView

urlpatterns = [
    path("", ProjectListCreateAPIView.as_view(), name="project-list-create"),
    path('<int:project_id>/', ProjectRetrieveUpdateDestroyAPIView.as_view(), name='project-detail'),
    path('<int:project_id>/contents/', include('user_app.contents.urls')),
]
