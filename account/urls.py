from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'account'

urlpatterns = [
    # ===============================
    # 🔐 AUTHENTICATION
    # ===============================
    path('login/', views.user_login, name='login'),                 # Alumni login
    path('admin/login/', views.admin_login, name='admin_login'),   # ✅ Admin login (NEW)
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('home/', views.home, name='home'),

    # ===============================
    # 📊 DASHBOARDS
    # ===============================
    path('dashboard/', views.alumni_dashboard, name='alumni_dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),  # ✅ FIXED PATH

    # ===============================
    # ⚙️ ACCOUNT SETTINGS
    # ===============================
    path('settings/', views.account_settings, name='account_settings'),

    # ===============================
    # 💼 EMPLOYMENT MANAGEMENT
    # ===============================
    path('employment/', views.employment_list, name='employment_list'),
    path('employment/add/', views.add_employment, name='add_employment'),
    path('employment/<int:employment_id>/edit/', views.edit_employment, name='edit_employment'),
    path('employment/<int:employment_id>/delete/', views.delete_employment, name='delete_employment'),

    # ===============================
    # 🎓 FURTHER STUDIES
    # ===============================
    path('studies/', views.studies_list, name='studies_list'),
    path('studies/add/', views.add_study, name='add_study'),
    path('studies/<int:study_id>/edit/', views.edit_study, name='edit_study'),
    path('studies/<int:study_id>/delete/', views.delete_study, name='delete_study'),

    # ===============================
    # 🔑 PASSWORD MANAGEMENT
    # ===============================
    path('password_change/',
         auth_views.PasswordChangeView.as_view(
             template_name='registration/password_change_form.html'
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
             email_template_name='registration/password_reset_email.html'
         ),
         name='password_reset'),

    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]