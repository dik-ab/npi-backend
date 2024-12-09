from django.urls import path

from user_app.accounts.views.account_views import AccountView, PasswordResetView, PasswordResetVerifyView, PasswordResetConfirmView

urlpatterns = [
    path("", AccountView.as_view(), name="account_create"),
    path("password_reset_token_generate/", PasswordResetView.as_view(), name="reset_token_generate"),
    path("password_reset_token_verify/", PasswordResetVerifyView.as_view(), name="reset_token_verify"),
    path("password_reset/", PasswordResetConfirmView.as_view(), name="reset_password"),
]
