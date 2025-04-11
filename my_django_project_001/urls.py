"""
URL configuration for my_django_project_001 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from django.shortcuts import render
from apps.users.views import SignupView, dashboard_view
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("apps.users.urls")),
    path('api/core/', include('apps.core.api.urls')),  # Ensure this includes core URLs
    path("signin/", lambda request: render(request, "signin.html"), name="signin"),
    path("signup/", SignupView.as_view(), name="signup"),
    path('', dashboard_view, name='dashboard'),  # Dashboard as root
    path('logout/', auth_views.LogoutView.as_view(next_page='/logout-confirm/'), name='logout'),
    path('logout-confirm/', TemplateView.as_view(template_name='logout_confirm.html'), name='logout_confirm'),
]
