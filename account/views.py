from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count, Q, F
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import datetime
 
from .auth_forms import LoginForm, AlumniRegistrationForm
from .models import Alumni, Employment, FurtherStudy, Activity, Program, EmploymentStatus, Feature, RegistrationPageContent
from .models1 import CarouselSlide, CoreValue, PageContent, SiteConfig

@login_required
def dashboard(request):
    return render(request, "account/User_Dashboard.html", {"section": "dashboard"})

# staff-only decorator
def staff_required(view_func):
    return login_required(user_passes_test(lambda u: u.is_staff)(view_func))

def log_activity(alumni, activity_type, description=None):
    """Helper function to log user activities"""
    Activity.objects.create(alumni=alumni, activity_type=activity_type, description=description)

def get_alumni_dashboard_context(alumni):
    """
    Helper function to gather all data needed for alumni dashboard
    Returns a context dictionary with all necessary information
    """
    current_employment = alumni.get_current_employment()
    all_employments = alumni.employments.all()
    further_studies = alumni.further_studies.all()
    recent_activities = alumni.activities.all()[:5]
    
    context = {
        'alumni': alumni,
        'profile_completion': alumni.get_profile_completion_percentage(),
        'missing_fields': alumni.get_missing_profile_fields(),
        'employment_count': alumni.get_employment_count(),
        'current_employment': current_employment,
        'all_employments': all_employments,
        'further_studies': further_studies,
        'recent_activities': recent_activities,
        'years_since_graduation': alumni.get_years_since_graduation(),
        'section': 'dashboard',
    }
    
    return context

@staff_required
def admin_dashboard(request):
    total_alumni = Alumni.objects.count()

    status_breakdown = (
        Alumni.objects.values("employment_status")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    by_program = (
        Alumni.objects.values("program")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    by_year = (
        Alumni.objects.values("graduation_year")
        .annotate(total=Count("id"))
        .order_by("graduation_year")
    )

    recent = Alumni.objects.order_by("-created_at")[:10]

    # Pass data to the template (design)
    context = {
        "total_alumni": total_alumni,
        "status_breakdown": list(status_breakdown),
        "by_program": list(by_program),
        "by_year": list(by_year),
        "recent": recent,
    }

    return render(request, "account/admin/dashboard.html", context)


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request,
                username=cd["username"],
                password=cd["password"]
            )

            if user is not None:
                if user.is_active:
                    login(request, user)

                    # role-based redirect
                    if user.is_staff:
                        return redirect("account:admin_dashboard")
                    else:
                        return redirect("account:alumni_dashboard")

                return HttpResponse("Disabled account")

            form.add_error(None, "Invalid Student ID or Password. Please try again.")
            return render(request, "registration/User_Login.html", {"form": form})

    else:
        form = LoginForm()

    return render(request, "registration/User_Login.html", {"form": form})

def user_logout(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("account:home")

def home(request):
    # Get slides from database
    slides = CarouselSlide.objects.filter(is_active=True).order_by('order')
    
    # Get values from database
    values = CoreValue.objects.filter(is_active=True).order_by('order')
    
    # Get page content
    about_hero_title = PageContent.objects.filter(section='about_hero').first()
    about_description = PageContent.objects.filter(section='about_description').first()
    mission = PageContent.objects.filter(section='mission').first()
    vision = PageContent.objects.filter(section='vision').first()
    
    # Get config
    config = SiteConfig.get_config()
    
    # Pass to template
    context = {
        'slides': slides,
        'slide_count': slides.count(),
        'values': values,
        'about_hero_title': about_hero_title,
        'about_description': about_description,
        'mission': mission,
        'vision': vision,
        'config': config,
    }
    
    return render(request, 'home.html', context)

def register(request):
    """Registration view with dynamic data from database"""
    if request.method == 'POST':
        form = AlumniRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! You can now login with your Student ID.')
            return redirect('account:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AlumniRegistrationForm()

    # Get all active programs from database
    programs = Program.objects.filter(is_active=True)
    
    # Get all active employment statuses from database
    employment_statuses = EmploymentStatus.objects.filter(is_active=True)
    
    # Get all active features from database
    features = Feature.objects.filter(is_active=True)
    
    # Get page content (or use defaults)
    page_content = RegistrationPageContent.objects.first()
    
    # Generate graduation years dynamically
    current_year = datetime.now().year
    graduation_years = list(range(current_year, 2010, -1))
    
    context = {
        'programs': programs,
        'employment_statuses': employment_statuses,
        'features': features,
        'page_content': page_content,
        'graduation_years': graduation_years,
    }
    
    return render(request, 'registration/User_Register.html', context)
    

@login_required
def alumni_dashboard(request):
    """Main alumni dashboard view"""
    try:
        alumni = request.user.alumni_profile
    except Alumni.DoesNotExist:
        messages.warning(request, "Please complete your alumni profile setup.")
        return redirect('account:account_settings')
    
    context = get_alumni_dashboard_context(alumni)
    return render(request, "account/User_Dashboard.html", context)
 
 
@login_required
def account_settings(request):
    """Alumni account settings and profile management"""
    try:
        alumni = request.user.alumni_profile
    except Alumni.DoesNotExist:
        messages.error(request, "Alumni profile not found.")
        return redirect('account:alumni_dashboard')
    
    if request.method == "POST":
        # Update profile information
        alumni.first_name = request.POST.get('first_name', alumni.first_name)
        alumni.last_name = request.POST.get('last_name', alumni.last_name)
        alumni.email = request.POST.get('email', alumni.email)
        alumni.contact_number = request.POST.get('contact_number', alumni.contact_number)
        alumni.current_job_title = request.POST.get('current_job_title', alumni.current_job_title)
        alumni.current_company = request.POST.get('current_company', alumni.current_company)
        alumni.seniority_level = request.POST.get('seniority_level', alumni.seniority_level)
        
        # Profile photo
        if 'profile_photo' in request.FILES:
            alumni.profile_photo = request.FILES['profile_photo']
        
        alumni.save()
        
        log_activity(alumni, 'PROFILE_UPDATE', 'Profile information updated')
        messages.success(request, "Your profile has been updated successfully!")
        return redirect('account:alumni_dashboard')
    
    context = {
        'alumni': alumni,
        'section': 'settings',
    }
    
    return render(request, 'account/Account_Settings.html', context)
 
 
@login_required
def employment_list(request):
    """List all employment records for the alumni"""
    try:
        alumni = request.user.alumni_profile
    except Alumni.DoesNotExist:
        messages.error(request, "Alumni profile not found.")
        return redirect('account:alumni_dashboard')
    
    employments = alumni.employments.all()
    
    context = {
        'alumni': alumni,
        'employments': employments,
        'section': 'employment',
    }
    
    return render(request, 'list/List_Employment.html', context)
 
 
@login_required
def add_employment(request):
    """Add new employment record"""
    try:
        alumni = request.user.alumni_profile
    except Alumni.DoesNotExist:
        messages.error(request, "Alumni profile not found.")
        return redirect('account:alumni_dashboard')
    
    if request.method == "POST":
        employment = Employment(alumni=alumni)
        employment.company_name = request.POST.get('company_name')
        employment.job_title = request.POST.get('job_title')
        employment.employment_type = request.POST.get('employment_type')
        employment.salary_range = request.POST.get('salary_range')
        employment.is_job_related = request.POST.get('is_job_related') == 'on'
        
        # Handle dates
        date_hired = request.POST.get('date_hired')
        if date_hired:
            employment.date_hired = date_hired
        
        employment.save()
        
        log_activity(alumni, 'EMPLOYMENT_ADD', f"Added employment at {employment.company_name}")
        messages.success(request, "Employment record added successfully!")
        return redirect('account:employment_list')
    
    context = {
        'alumni': alumni,
        'section': 'employment',
    }
    
    return render(request, 'add/Add_Employment.html', context)
 
 
@login_required
def edit_employment(request, employment_id):
    """Edit employment record"""
    try:
        alumni = request.user.alumni_profile
    except Alumni.DoesNotExist:
        messages.error(request, "Alumni profile not found.")
        return redirect('account:alumni_dashboard')
    
    employment = get_object_or_404(Employment, id=employment_id, alumni=alumni)
    
    if request.method == "POST":
        employment.company_name = request.POST.get('company_name', employment.company_name)
        employment.job_title = request.POST.get('job_title', employment.job_title)
        employment.employment_type = request.POST.get('employment_type', employment.employment_type)
        employment.salary_range = request.POST.get('salary_range', employment.salary_range)
        employment.is_job_related = request.POST.get('is_job_related') == 'on'
        
        date_hired = request.POST.get('date_hired')
        if date_hired:
            employment.date_hired = date_hired
        
        employment.save()
        
        log_activity(alumni, 'EMPLOYMENT_UPDATE', f"Updated employment at {employment.company_name}")
        messages.success(request, "Employment record updated successfully!")
        return redirect('account:employment_list')
    
    context = {
        'alumni': alumni,
        'employment': employment,
        'section': 'employment',
    }
    
    return render(request, 'edit/Edit_Employment.html', context)
 
 
@login_required
@require_http_methods(["POST"])
def delete_employment(request, employment_id):
    """Delete employment record"""
    try:
        alumni = request.user.alumni_profile
    except Alumni.DoesNotExist:
        messages.error(request, "Alumni profile not found.")
        return redirect('account:alumni_dashboard')
    
    employment = get_object_or_404(Employment, id=employment_id, alumni=alumni)
    company_name = employment.company_name
    employment.delete()
    
    messages.success(request, f"Employment record at {company_name} has been deleted.")
    return redirect('account:employment_list')
 
 
@login_required
def studies_list(request):
    """List further studies records"""
    try:
        alumni = request.user.alumni_profile
    except Alumni.DoesNotExist:
        messages.error(request, "Alumni profile not found.")
        return redirect('account:alumni_dashboard')
    
    studies = alumni.further_studies.all()
    
    context = {
        'alumni': alumni,
        'studies': studies,
        'section': 'studies',
    }
    
    return render(request, 'list/List_Studies.html', context)
 
 
@login_required
def add_study(request):
    """Add further study record"""
    try:
        alumni = request.user.alumni_profile
    except Alumni.DoesNotExist:
        messages.error(request, "Alumni profile not found.")
        return redirect('account:alumni_dashboard')
    
    if request.method == "POST":
        study = FurtherStudy(alumni=alumni)
        study.school_name = request.POST.get('school_name')
        study.program = request.POST.get('program')
        study.field_of_study = request.POST.get('field_of_study')
        study.status = request.POST.get('status', 'ONGOING')
        study.description = request.POST.get('description')
        study.school_website = request.POST.get('school_website')
        
        start_year = request.POST.get('start_year')
        if start_year:
            study.start_year = int(start_year)
        
        end_year = request.POST.get('end_year')
        if end_year and study.status != 'ONGOING':
            study.end_year = int(end_year)
        
        study.save()
        
        # Update alumni employment status if pursuing studies
        if study.status == 'ONGOING':
            alumni.employment_status = 'STUDENT'
            alumni.save()
        
        log_activity(alumni, 'STUDY_ADD', f"Added study program: {study.program}")
        messages.success(request, "Study record added successfully!")
        return redirect('account:studies_list')
    
    context = {
        'alumni': alumni,
        'section': 'studies',
    }
    
    return render(request, 'add/Add_Studies.html', context)
 
 
@login_required
def edit_study(request, study_id):
    """Edit further study record"""
    try:
        alumni = request.user.alumni_profile
    except Alumni.DoesNotExist:
        messages.error(request, "Alumni profile not found.")
        return redirect('account:alumni_dashboard')
    
    study = get_object_or_404(FurtherStudy, id=study_id, alumni=alumni)
    
    if request.method == "POST":
        study.school_name = request.POST.get('school_name', study.school_name)
        study.program = request.POST.get('program', study.program)
        study.field_of_study = request.POST.get('field_of_study', study.field_of_study)
        study.status = request.POST.get('status', study.status)
        study.description = request.POST.get('description', study.description)
        study.school_website = request.POST.get('school_website', study.school_website)
        
        start_year = request.POST.get('start_year')
        if start_year:
            study.start_year = int(start_year)
        
        end_year = request.POST.get('end_year')
        if end_year:
            study.end_year = int(end_year)
        
        study.save()
        
        log_activity(alumni, 'STUDY_UPDATE', f"Updated study program: {study.program}")
        messages.success(request, "Study record updated successfully!")
        return redirect('account:studies_list')
    
    context = {
        'alumni': alumni,
        'study': study,
        'section': 'studies',
    }
    
    return render(request, 'edit/Edit_Studies.html', context)
 
 
@login_required
@require_http_methods(["POST"])
def delete_study(request, study_id):
    """Delete further study record"""
    try:
        alumni = request.user.alumni_profile
    except Alumni.DoesNotExist:
        messages.error(request, "Alumni profile not found.")
        return redirect('account:alumni_dashboard')
    
    study = get_object_or_404(FurtherStudy, id=study_id, alumni=alumni)
    program_name = study.program
    study.delete()
    
    messages.success(request, f"Study record for {program_name} has been deleted.")
    return redirect('account:studies_list')