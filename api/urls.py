from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, user_profile, logout, refresh_token

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', user_profile, name='user_profile'),
    path('logout/', logout, name='logout'),
    path('token/refresh/', refresh_token, name='token_refresh'),
]

