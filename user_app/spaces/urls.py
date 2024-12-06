from django.urls import path, include
from user_app.spaces.views import SpaceListView

urlpatterns = [
    path("", SpaceListView.as_view(), name="spaces-list"),
    path('<int:space_id>/projects/', include('user_app.projects.urls')),
]
