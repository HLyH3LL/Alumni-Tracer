from django.urls import path
from django.contrib.auth import views as auth_views
from . import views   

app_name = 'account'

urlpatterns = [
    # Authentication
    path('login/', views.user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        template_name='registration/logout.html'
    ), name='logout'),
    
    # Add this line - make sure it's BEFORE the password URLs
    path('register/', views.register, name='register'),

    # Dashboards
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Account/Profile management
    path('account/', views.account_view, name='account'),
    path('account/change-password/', views.change_password, name='change_password'),

    # Password management
    path('password_change/',
         auth_views.PasswordChangeView.as_view(
             template_name='registration/password_change_form.html',
             success_url='done/'
         ),
         name='password_change'),
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='registration/password_change_done.html'
         ),
         name='password_change_done'),
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',
             success_url='done/'
         ),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url='done/'
         ),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]