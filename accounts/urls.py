from django.urls import path

from .views.account_views import AccountView
from .views.auth_views import LoginView, LogoutView, RefreshTokenView

urlpatterns = [
    path("", AccountView.as_view(), name="account_list_create"),
    path("<int:pk>/", AccountView.as_view(), name="account_detail_update_delete"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", RefreshTokenView.as_view(), name="refresh"),
]
