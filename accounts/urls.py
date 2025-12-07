from django.urls import path
from django.contrib.auth.views import LoginView
from .views import register, logout_view, admin_dashboard

urlpatterns = [
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
]
