from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from datetime import datetime

from .auth_forms import LoginForm, AlumniRegistrationForm
from .models import Alumni, Employment, FurtherStudy, Activity, Program, EmploymentStatus, Feature, RegistrationPageContent
from .models1 import CarouselSlide, CoreValue, PageContent, SiteConfig


# ===============================
# ✅ STAFF DECORATOR
# ===============================
def staff_required(view_func):
    return login_required(user_passes_test(lambda u: u.is_staff)(view_func))


# ===============================
# ✅ ADMIN LOGIN (NEW)
# ===============================
def admin_login(request):
    # 🔥 Redirect if already logged in
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("account:admin_dashboard")
        return redirect("account:alumni_dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active and user.is_staff:
                login(request, user)
                return redirect("account:admin_dashboard")
            else:
                messages.error(request, "You are not authorized as admin.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "account/admin/admin_login.html")


# ===============================
# ✅ USER LOGIN (UPDATED)
# ===============================
def user_login(request):
    # 🔥 Redirect if already logged in
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("account:admin_dashboard")
        return redirect("account:alumni_dashboard")

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

                    # ❌ BLOCK ADMINS HERE
                    if user.is_staff:
                        messages.error(request, "Please use the admin login page.")
                        return redirect("account:admin_login")

                    login(request, user)
                    next_url = request.GET.get('next') or request.POST.get('next')
                    if next_url:
                        return redirect(next_url)
                    return redirect("account:alumni_dashboard")

                return HttpResponse("Disabled account")

            form.add_error(None, "Invalid Student ID or Password. Please try again.")
            return render(request, "registration/User_Login.html", {"form": form})

    else:
        form = LoginForm()

    return render(request, "registration/User_Login.html", {"form": form})


# ===============================
# ✅ ADMIN DASHBOARD
# ===============================
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

    context = {
        "total_alumni": total_alumni,
        "status_breakdown": list(status_breakdown),
        "by_program": list(by_program),
        "by_year": list(by_year),
        "recent": recent,
    }

    return render(request, "account/admin/dashboard.html", context)


# ===============================
# ✅ USER LOGOUT
# ===============================
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("account:home")


# ===============================
# ✅ ALUMNI DASHBOARD
# ===============================
@login_required
def alumni_dashboard(request):
    try:
        alumni = request.user.alumni_profile
    except Alumni.DoesNotExist:
        # Create basic Alumni profile if it doesn't exist
        alumni = Alumni.objects.create(
            user=request.user,
            student_id=request.user.username,
            first_name=request.user.first_name,
            last_name=request.user.last_name,
            email=request.user.email,
            program='',
            graduation_year=0,
            employment_status='UNKNOWN'
        )
        messages.info(request, "Please complete your alumni profile information.")

    context = {
        'alumni': alumni,
        'section': 'dashboard',
    }
    return render(request, "account/User_Dashboard.html", context)



@login_required
def account_settings(request):
    try:
        alumni = request.user.alumni_profile
    except Alumni.DoesNotExist:
        # Create basic Alumni profile if it doesn't exist
        alumni = Alumni.objects.create(
            user=request.user,
            student_id=request.user.username,
            first_name=request.user.first_name,
            last_name=request.user.last_name,
            email=request.user.email,
            program='',
            graduation_year=0,
            employment_status='UNKNOWN'
        )
        messages.info(request, "Please complete your alumni profile information.")

    return render(request, "account/account_settings.html", {
        "alumni": alumni
    })






# ===============================
# ✅ HOME
# ===============================
def home(request):
    slides = CarouselSlide.objects.filter(is_active=True).order_by('order')
    values = CoreValue.objects.filter(is_active=True).order_by('order')

    about_hero_title = PageContent.objects.filter(section='about_hero').first()
    about_description = PageContent.objects.filter(section='about_description').first()
    mission = PageContent.objects.filter(section='mission').first()
    vision = PageContent.objects.filter(section='vision').first()

    config = SiteConfig.get_config()

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


# ===============================
# ✅ REGISTER
# ===============================
def register(request):
    if request.method == 'POST':
        form = AlumniRegistrationForm(request.POST)

        # ✅ FIX (IMPORTANT)
        form.fields['program'].queryset = Program.objects.all()
        form.fields['employment_status'].queryset = EmploymentStatus.objects.all()

        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful!')
            return redirect('account:login')
        else:
            print(form.errors)
            messages.error(request, 'Please correct the errors below.')
 
    else:
        form = AlumniRegistrationForm()

        # ✅ ADD ALSO HERE (IMPORTANT)
        form.fields['program'].queryset = Program.objects.all()
        form.fields['employment_status'].queryset = EmploymentStatus.objects.all()

    programs = Program.objects.filter(is_active=True)
    employment_statuses = EmploymentStatus.objects.filter(is_active=True)
    features = Feature.objects.filter(is_active=True)
    page_content = RegistrationPageContent.objects.first()

    current_year = datetime.now().year
    graduation_years = list(range(current_year, 2010, -1))

    return render(request, 'registration/User_Register.html', {
        'form': form,
        'programs': programs,
        'employment_statuses': employment_statuses,
        'features': features,
        'page_content': page_content,
        'graduation_years': graduation_years,
    })


# ===============================
# ✅ EMPLOYMENT CRUD (minimal safe stubs)
# ===============================
@login_required
def employment_list(request):
    try:
        alumni = request.user.alumni_profile
    except Alumni.DoesNotExist:
        messages.warning(request, "Please complete your alumni profile setup.")
        return redirect('account:account_settings')

    employments = Employment.objects.filter(alumni=alumni).order_by('-date_hired')
    studies = FurtherStudy.objects.filter(alumni=alumni).order_by('-start_year')

    return render(request, 'account/User_Dashboard.html', {
        'alumni': alumni,
        'all_employments': employments,
        'further_studies': studies,
        'employment_count': employments.count(),
        'recent_activities': Activity.objects.filter(alumni=alumni).order_by('-created_at')[:10],
        'profile_completion': 75,
        'missing_fields': [],
        'section': 'employment'
    })


@login_required
def add_employment(request):
    try:
        alumni = request.user.alumni_profile
    except Alumni.DoesNotExist:
        messages.warning(request, "Please complete your alumni profile setup.")
        return redirect('account:account_settings')

    if request.method == 'POST':
        company = request.POST.get('company_name', '').strip()
        title = request.POST.get('job_title', '').strip()
        date_hired = request.POST.get('date_hired') or None
        created_via_voice = request.POST.get('created_via_voice') == 'on'
        voice_transcript = request.POST.get('voice_transcript', '').strip() or None

        Employment.objects.create(
            alumni=alumni,
            company_name=company,
            job_title=title,
            date_hired=date_hired,
            created_via_voice=created_via_voice,
            voice_transcript=voice_transcript,
            voice_updated=False,
        )
        messages.success(request, 'Employment record added.')
        return redirect('account:employment_list')

    return render(request, 'forms/Employment_Form.html')


@login_required
def edit_employment(request, employment_id):
    try:
        alumni = request.user.alumni_profile
    except Alumni.DoesNotExist:
        messages.warning(request, "Please complete your alumni profile setup.")
        return redirect('account:account_settings')

    employment = get_object_or_404(Employment, pk=employment_id, alumni=alumni)

    if request.method == 'POST':
        employment.company_name = request.POST.get('company_name', employment.company_name)
        employment.job_title = request.POST.get('job_title', employment.job_title)
        employment.date_hired = request.POST.get('date_hired') or employment.date_hired
        employment.save()
        messages.success(request, 'Employment record updated.')
        return redirect('account:employment_list')

    return render(request, 'forms/Employment_Form.html', {'employment': employment})


@login_required
def delete_employment(request, employment_id):
    try:
        alumni = request.user.alumni_profile
    except Alumni.DoesNotExist:
        messages.warning(request, "Please complete your alumni profile setup.")
        return redirect('account:account_settings')

    employment = get_object_or_404(Employment, pk=employment_id, alumni=alumni)
    if request.method == 'POST':
        employment.delete()
        messages.success(request, 'Employment record deleted.')
        return redirect('account:employment_list')

    return render(request, 'account/confirm_delete_employment.html', {'employment': employment})


# ===============================
# ✅ FURTHER STUDIES CRUD (minimal safe stubs)
# ===============================
@login_required
def studies_list(request):
    try:
        alumni = request.user.alumni_profile
    except Alumni.DoesNotExist:
        messages.warning(request, "Please complete your alumni profile setup.")
        return redirect('account:account_settings')

    employments = Employment.objects.filter(alumni=alumni).order_by('-date_hired')
    studies = FurtherStudy.objects.filter(alumni=alumni).order_by('-start_year')

    return render(request, 'account/User_Dashboard.html', {
        'alumni': alumni,
        'all_employments': employments,
        'further_studies': studies,
        'employment_count': employments.count(),
        'recent_activities': Activity.objects.filter(alumni=alumni).order_by('-created_at')[:10],
        'profile_completion': 75,
        'missing_fields': [],
        'section': 'studies'
    })


@login_required
def add_study(request):
    try:
        alumni = request.user.alumni_profile
    except Alumni.DoesNotExist:
        messages.warning(request, "Please complete your alumni profile setup.")
        return redirect('account:account_settings')

    if request.method == 'POST':
        school = request.POST.get('school_name', '').strip()
        program = request.POST.get('program', '').strip()
        start_year = request.POST.get('start_year') or None
        created_via_voice = request.POST.get('created_via_voice') == 'on'
        voice_transcript = request.POST.get('voice_transcript', '').strip() or None

        FurtherStudy.objects.create(
            alumni=alumni,
            school_name=school,
            program=program,
            start_year=start_year,
            created_via_voice=created_via_voice,
            voice_transcript=voice_transcript,
            voice_updated=False,
        )
        messages.success(request, 'Study record added.')
        return redirect('account:studies_list')

    return render(request, 'forms/Study_Form.html')


@login_required
def edit_study(request, study_id):
    try:
        alumni = request.user.alumni_profile
    except Alumni.DoesNotExist:
        messages.warning(request, "Please complete your alumni profile setup.")
        return redirect('account:account_settings')

    study = get_object_or_404(FurtherStudy, pk=study_id, alumni=alumni)

    if request.method == 'POST':
        study.school_name = request.POST.get('school_name', study.school_name)
        study.program = request.POST.get('program', study.program)
        study.start_year = request.POST.get('start_year') or study.start_year
        study.end_year = request.POST.get('end_year') or study.end_year
        study.is_ongoing = bool(request.POST.get('is_ongoing', study.is_ongoing))
        study.save()
        messages.success(request, 'Study record updated.')
        return redirect('account:studies_list')

    return render(request, 'forms/Study_Form.html', {'study': study})


@login_required
def delete_study(request, study_id):
    try:
        alumni = request.user.alumni_profile
    except Alumni.DoesNotExist:
        messages.warning(request, "Please complete your alumni profile setup.")
        return redirect('account:account_settings')

    study = get_object_or_404(FurtherStudy, pk=study_id, alumni=alumni)
    if request.method == 'POST':
        study.delete()
        messages.success(request, 'Study record deleted.')
        return redirect('account:studies_list')

    return render(request, 'account/confirm_delete_study.html', {'study': study})
# ===============================
# 🛠️ ADMIN FEATURES (SIDEBAR)
# ===============================

@staff_required
def alumni_records(request):
    alumni_list = Alumni.objects.all().order_by('-created_at')

    return render(request, 'account/admin/alumni_records.html', {
        'alumni_list': alumni_list
    })

@staff_required
def add_alumni(request):
    from .auth_forms import AdminAlumniForm

    if request.method == 'POST':
        form = AdminAlumniForm(request.POST)
        if form.is_valid():
            alumni = form.save(commit=False)
            alumni.save()
            messages.success(request, 'Alumni record added successfully.')
            return redirect('account:alumni_records')
    else:
        form = AdminAlumniForm()

    return render(request, 'account/admin/alumni_form.html', {'form': form, 'title': 'Add Alumni'})


@staff_required
def edit_alumni(request, alumni_id):
    from .auth_forms import AdminAlumniForm

    alumni = get_object_or_404(Alumni, pk=alumni_id)

    if request.method == 'POST':
        form = AdminAlumniForm(request.POST, instance=alumni)
        if form.is_valid():
            form.save()
            messages.success(request, 'Alumni record updated successfully.')
            return redirect('account:alumni_records')
    else:
        form = AdminAlumniForm(instance=alumni)

    return render(request, 'account/admin/alumni_form.html', {'form': form, 'title': 'Edit Alumni'})


@staff_required
def delete_alumni(request, alumni_id):
    alumni = get_object_or_404(Alumni, pk=alumni_id)

    if request.method == 'POST':
        alumni.delete()
        messages.success(request, 'Alumni record deleted successfully.')
        return redirect('account:alumni_records')

    return render(request, 'account/admin/confirm_delete_alumni.html', {'alumni': alumni})


@staff_required
def profile_verification(request):
    pending_alumni = Alumni.objects.filter(is_verified=False)

    return render(request, 'account/admin/profile_verification.html', {
        'pending_alumni': pending_alumni
    })
@staff_required
def approve_alumni(request, id):
    alumni = get_object_or_404(Alumni, id=id)
    alumni.is_verified = True
    alumni.save()
    messages.success(request, "Alumni approved successfully.")
    return redirect('account:profile_verification')


@staff_required
def reject_alumni(request, id):
    alumni = get_object_or_404(Alumni, id=id)
    alumni.delete()
    messages.warning(request, "Alumni rejected and removed.")
    return redirect('account:profile_verification')


@staff_required
def announcements(request):
    return render(request, 'account/admin/announcements.html')


@staff_required
def reports(request):
    return render(request, 'account/admin/reports.html')


@staff_required
def user_management(request):
    return render(request, 'account/admin/user_management.html')


@staff_required
def admin_settings(request):
    return render(request, 'account/admin/settings.html')


from django.shortcuts import render

def terms_conditions(request):
    config = {
        'company_name': 'T.I.P.ians Connect',
        'tagline': 'Connecting TIP alumni',
    }
    return render(request, 'account/TERMS_AND_CONDITIONS.html', {'config': config})

def privacy_policy(request):
    config = {
        'company_name': 'T.I.P.ians Connect',
        'tagline': 'Connecting TIP alumni',
    }
    return render(request, 'account/PRIVACY_POLICY.html', {'config': config})


