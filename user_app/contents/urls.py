from django.urls import path
from user_app.contents.views import ContentsListCreateAPIView, ContentsRetrieveReproduceUpdateDestroyAPIView

urlpatterns = [
    path("", ContentsListCreateAPIView.as_view(), name="contents-list-create"),
    path('<int:contents_id>/', ContentsRetrieveReproduceUpdateDestroyAPIView.as_view(), name='contents-detail'),
]