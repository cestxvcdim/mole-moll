from django.contrib.auth.views import LogoutView
from django.urls import path

from users.apps import UsersConfig
from users import views

app_name = UsersConfig.name

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('confirm_register/<str:token>/', views.RegisterConfirmView.as_view(), name='confirm_register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('password_reset/', views.UserPasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', views.UserPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', views.UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', views.UserPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('all/', views.UserListView.as_view(), name='user_list'),
    path('all/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('all/<int:pk>/update/', views.UserUpdateView.as_view(), name='user_update'),
]
