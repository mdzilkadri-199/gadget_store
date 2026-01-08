# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('user/', views.dashboard_user, name='dashboard_user'),
    path('admin/', views.dashboard_admin, name='dashboard_admin'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', 
         auth_views.LoginView.as_view(
             template_name='accounts/login.html',
             redirect_authenticated_user=True
         ), 
         name='login'),
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), 
         name='password_reset'),
    path('logout/', 
         auth_views.LogoutView.as_view(next_page='/'), 
         name='logout'),
]