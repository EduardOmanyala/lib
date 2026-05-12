from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    user_profile,
    logout,
    refresh_token,
    confirm_email,
    get_current_user,
    password_reset_request,
    password_reset_confirm,
)

urlpatterns = [
    path('confirm-email/<uidb64>/<str:token>/', confirm_email, name='confirm_email'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', user_profile, name='user_profile'),
    path('logout/', logout, name='logout'),
    path('token/refresh/', refresh_token, name='token_refresh'),
    path('user/', get_current_user),
    path('password-reset/', password_reset_request, name='password_reset_request'),
    path('password-reset/<uidb64>/<str:token>/', password_reset_confirm, name='password_reset_confirm'),
]

