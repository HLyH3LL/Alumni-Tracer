from django.urls import path
from . import views, voice_views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

app_name = 'account'

urlpatterns = [
    # ===============================
    # 🔐 AUTHENTICATION
    # ===============================
    path('login/', views.user_login, name='login'),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('home/', views.home, name='home'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),
    path('save-face/', views.save_face, name='save_face'),
    path('face-login/', views.face_login, name='face_login'),

    # ===============================
    # 📊 DASHBOARDS
    # ===============================
    path('dashboard/', views.alumni_dashboard, name='alumni_dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # ===============================
    # 🛠️ ADMIN FEATURES (SIDEBAR)
    # ===============================
    path('admin/alumni-records/', views.alumni_records, name='alumni_records'),
    path('admin/alumni-records/add/', views.add_alumni, name='add_alumni'),
    path('admin/alumni-records/<int:alumni_id>/edit/', views.edit_alumni, name='edit_alumni'),
    path('admin/alumni-records/<int:alumni_id>/delete/', views.delete_alumni, name='delete_alumni'),
    path('admin/profile-verification/', views.profile_verification, name='profile_verification'),
    path('admin/approve-alumni/<int:id>/', views.approve_alumni, name='approve_alumni'),
    path('admin/reject-alumni/<int:id>/', views.reject_alumni, name='reject_alumni'),
    path('admin/announcements/', views.announcements, name='announcements'),
    path('admin/reports/', views.reports, name='reports'),
    path('admin/user-management/', views.user_management, name='user_management'),
    path('admin/settings/', views.admin_settings, name='admin_settings'),

    # ===============================
    # ⚙️ ACCOUNT SETTINGS (USER)
    # ===============================
    path('settings/', views.account_settings, name='account_settings'),

    # ✅ 🔥 SAFE FIX (IMPORTANT — prevents NoReverseMatch)
    path('settings-fallback/', views.account_settings, name='settings'),

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
    # 📜 TERMS AND CONDITIONS & PRIVACY POLICY
    # ===============================
    path('terms/', views.terms_conditions, name='terms_and_conditions'),   # legacy alias
    path('privacy/', views.privacy_policy, name='privacy_policy'),       
    
    # ===============================
    # 🔑 PASSWORD MANAGEMENT
    # ===============================
    path('password_change/',
         auth_views.PasswordChangeView.as_view(
             template_name='registration/password_change_form.html',
             success_url='/account/password_change/done/'   # absolute path
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

    # ===============================
    # 🎤 VOICE UPDATE
    # ===============================
    path('voice-update/', voice_views.voice_update, name='voice_update'),

]