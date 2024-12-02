"""
URL configuration for npi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include

from mail_templates.views import SendMailView
from accounts.views.account_views import MeView, Generate2FAView, Verify2FAView
from accounts.views.auth_views import LoginView, LogoutView, RefreshTokenView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("me/", MeView.as_view(), name="me"),
    path('me/2fa-generate/', Generate2FAView.as_view(), name='2fa-generate'),
    path('me/2fa-verify/', Verify2FAView.as_view(), name='2fa-verify'),
    path("accounts/", include("accounts.urls")),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("refresh/", RefreshTokenView.as_view(), name="refresh"),
    path("send-mail/", SendMailView.as_view(), name="send-mail"),
    path("health", lambda request: HttpResponse(status=200), name="health_check"),
]
