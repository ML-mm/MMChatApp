# chat/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = "mainchat"

urlpatterns = [
    path("", views.home, name="home"),
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('rooms/<str:room_name>/', views.room_view, name='room'),
]