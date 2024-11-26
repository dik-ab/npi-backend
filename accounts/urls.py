from django.urls import path

from accounts.views.account_views import AccountView

urlpatterns = [
    path("", AccountView.as_view(), name="account_create"),
]
