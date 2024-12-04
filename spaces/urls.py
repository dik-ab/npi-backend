from django.urls import path, include
from .views import SpaceListView

urlpatterns = [
    path("", SpaceListView.as_view(), name="spaces-list"),
    path('<int:space_id>/projects/', include('projects.urls')),
]
