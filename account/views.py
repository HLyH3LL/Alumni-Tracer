from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from datetime import datetime
from types import SimpleNamespace

from .auth_forms import LoginForm, AlumniRegistrationForm
from .models import Alumni, Employment, FurtherStudy, Activity, Program, EmploymentStatus, Feature, RegistrationPageContent
from .models1 import CarouselSlide, CoreValue, PageContent, SiteConfig


# ===============================
# ✅ STAFF DECORATOR
# ===============================
def staff_required(view_func):
    return login_required(user_passes_test(lambda u: u.is_staff)(view_func))


def get_or_create_alumni_profile(user):
    """
    Ensure logged-in users can use employment/study forms even without
    a pre-existing alumni profile by creating a minimal fallback profile.
    """
    try:
        return user.alumni_profile
    except Alumni.DoesNotExist:
        fallback_student_id = (user.username or f"user{user.id}")[:30]
        fallback_first_name = (user.first_name or user.username or "User")[:80]
        fallback_last_name = (user.last_name or "Alumni")[:80]

        # Resolve potential student_id collisions.
        unique_student_id = fallback_student_id
        suffix = 1
        while Alumni.objects.filter(student_id=unique_student_id).exists():
            suffix_str = str(suffix)
            unique_student_id = f"{fallback_student_id[:30-len(suffix_str)]}{suffix_str}"
            suffix += 1

        return Alumni.objects.create(
            user=user,
            student_id=unique_student_id,
            first_name=fallback_first_name,
            last_name=fallback_last_name,
            email=user.email or None,
            program="Not Specified",
            graduation_year=datetime.now().year,
            employment_status="UNKNOWN",
        )


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

                    if user.is_staff:
                        messages.error(request, "Please use the admin login page.")
                        return redirect("account:admin_login")

                    login(request, user)
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
    """Main alumni dashboard view"""
    try:
        alumni = request.user.alumni_profile
    except Alumni.DoesNotExist:
        messages.warning(request, "Profile data is not available yet. Showing an empty dashboard.")
        context = {
            "alumni": SimpleNamespace(student_id=None, graduation_year=None, seniority_level="Unknown"),
            "profile_completion": 0,
            "missing_fields": ["Profile Information"],
            "profile_checklist": [],
            "employment_count": 0,
            "current_employment": None,
            "all_employments": [],
            "further_studies": [],
            "recent_activities": [],
            "years_since_graduation": 0,
            "career_timeline": [],
            "total_years_employed": 0,
            "first_job_date": None,
            "latest_job_date": None,
            "section": "dashboard",
        }
        return render(request, "account/User_Dashboard.html", context)
    
    # ✅ MUST call this to get employment data!
    context = get_alumni_dashboard_context(alumni)
    
    # ✅ MUST pass context to template!
    return render(request, "account/User_Dashboard.html", context)



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
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful!')
            return redirect('account:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AlumniRegistrationForm()

    programs = Program.objects.filter(is_active=True)
    employment_statuses = EmploymentStatus.objects.filter(is_active=True)
    features = Feature.objects.filter(is_active=True)
    page_content = RegistrationPageContent.objects.first()

    current_year = datetime.now().year
    graduation_years = list(range(current_year, 2010, -1))

    context = {
        'form': form,
        'programs': programs,
        'employment_statuses': employment_statuses,
        'features': features,
        'page_content': page_content,
        'graduation_years': graduation_years,
    }

    return render(request, 'registration/User_Register.html', context)


# ===============================
# ✅ EMPLOYMENT CRUD (minimal safe stubs)
# ===============================
@login_required
def employment_list(request):
    alumni = get_or_create_alumni_profile(request.user)

    employments = Employment.objects.filter(alumni=alumni).order_by('-date_hired')
    return render(request, 'account/employment_list.html', {'employments': employments})


@login_required
def add_employment(request):
    """Add a new employment record for the logged-in alumni"""
    alumni = get_or_create_alumni_profile(request.user)

    if request.method == "POST":
        try:
            with transaction.atomic():
                # Get and validate form data
                company_name = request.POST.get("company_name", "").strip()
                job_title = request.POST.get("job_title", "").strip()
                date_hired = request.POST.get("date_hired") or None
                date_left = request.POST.get("date_left") or None
                
                # Validate required fields
                if not company_name or not job_title:
                    messages.error(request, "Company name and job title are required.")
                    return render(request, "forms/Base_Form.html", {
                        "type": "employment",
                        "object": None
                    })
                
                # Validate date logic
                if date_hired and date_left:
                    if date_hired > date_left:
                        messages.error(request, "Start date must be before end date.")
                        return render(request, "forms/Base_Form.html", {
                            "type": "employment",
                            "object": None
                        })
                
                # Create employment record
                emp = Employment.objects.create(
                    alumni=alumni,
                    company_name=company_name,
                    job_title=job_title,
                    employment_type=request.POST.get("employment_type") or None,
                    salary_range=request.POST.get("salary_range") or None,
                    is_job_related=request.POST.get("is_job_related") == "on",
                    date_hired=date_hired,
                    date_left=date_left,
                )
                
                # Log activity
                Activity.objects.create(
                    alumni=alumni,
                    activity_type="EMPLOYMENT_ADD",
                    description=f"Added employment at {company_name} as {job_title}"
                )
                
                # Show success message
                messages.success(
                    request, 
                    f"Employment at {company_name} added successfully!"
                )
                
                return redirect("account:alumni_dashboard")
                
        except Exception as e:
            messages.error(request, f"Error saving employment: {str(e)}")
            return render(request, "forms/Base_Form.html", {
                "type": "employment",
                "object": None
            })

    return render(request, "forms/Base_Form.html", {
        "type": "employment",
        "object": None
    })

@login_required
def edit_employment(request, employment_id):
    """Edit an employment record"""
    alumni = get_or_create_alumni_profile(request.user)

    # Get the employment record
    emp = get_object_or_404(Employment, id=employment_id, alumni=alumni)

    if request.method == "POST":
        try:
            with transaction.atomic():
                # Validate required fields
                company_name = request.POST.get("company_name", "").strip()
                job_title = request.POST.get("job_title", "").strip()

                if not company_name or not job_title:
                    messages.error(request, "Company and job title are required.")
                    return render(request, "forms/Base_Form.html", {
                        "type": "employment",
                        "object": emp
                    })

                # Get dates
                date_hired = request.POST.get("date_hired") or None
                date_left = request.POST.get("date_left") or None

                # Validate date logic
                if date_hired and date_left:
                    if date_hired > date_left:
                        messages.error(request, "Start date must be before end date.")
                        return render(request, "forms/Base_Form.html", {
                            "type": "employment",
                            "object": emp
                        })

                # Update the record
                emp.company_name = company_name
                emp.job_title = job_title
                emp.employment_type = request.POST.get("employment_type") or None
                emp.salary_range = request.POST.get("salary_range") or None
                emp.is_job_related = request.POST.get("is_job_related") == "on"
                emp.date_hired = date_hired
                emp.date_left = date_left
                emp.save()

                # Log activity
                Activity.objects.create(
                    alumni=alumni,
                    activity_type="EMPLOYMENT_UPDATE",
                    description=f"Updated employment at {company_name}"
                )

                messages.success(request, f"{company_name} updated successfully!")
                return redirect("account:alumni_dashboard")

        except Exception as e:
            messages.error(request, f"Error updating employment: {str(e)}")
            return render(request, "forms/Base_Form.html", {
                "type": "employment",
                "object": emp
            })

    return render(request, "forms/Base_Form.html", {
        "type": "employment",
        "object": emp
    })


def _wants_json(request):
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


@login_required
def delete_employment(request, employment_id):
    """Delete an employment record (POST only; use AJAX from dashboard/forms for modal flow)."""
    alumni = get_or_create_alumni_profile(request.user)
    emp = get_object_or_404(Employment, id=employment_id, alumni=alumni)

    if request.method != "POST":
        messages.info(request, "Use the delete button on your dashboard to remove a job.")
        return redirect("account:alumni_dashboard")

    try:
        company_name = emp.company_name
        emp.delete()
        Activity.objects.create(
            alumni=alumni,
            activity_type="EMPLOYMENT_DELETE",
            description=f"Deleted employment: {company_name}",
        )
        if _wants_json(request):
            return JsonResponse({"ok": True, "message": f"{company_name} was deleted."})
        messages.success(request, f"{company_name} deleted successfully!")
    except Exception as e:
        if _wants_json(request):
            return JsonResponse({"ok": False, "message": str(e)}, status=400)
        messages.error(request, f"Error deleting employment: {str(e)}")
    return redirect("account:alumni_dashboard")

# ===============================
# ✅ FURTHER STUDIES CRUD (minimal safe stubs)
# ===============================
@login_required
def studies_list(request):
    alumni = get_or_create_alumni_profile(request.user)

    studies = FurtherStudy.objects.filter(alumni=alumni).order_by('-start_year')
    return render(request, 'account/studies_list.html', {'studies': studies})


@login_required
def add_study(request):
    """Add a new further study record for the logged-in alumni"""
    alumni = get_or_create_alumni_profile(request.user)

    if request.method == "POST":
        try:
            with transaction.atomic():
                # Validate required fields
                school_name = request.POST.get("school_name", "").strip()
                program = request.POST.get("program", "").strip()
                start_year = request.POST.get("start_year")
                status = request.POST.get("status")
                
                if not school_name or not program or not start_year:
                    messages.error(request, "School, program, and start year are required.")
                    return render(request, "forms/Base_Form.html", {
                        "type": "study",
                        "object": None
                    })
                
                # Validate completion logic
                if status == "COMPLETED" and not request.POST.get("end_year"):
                    messages.error(request, "End year is required for completed programs.")
                    return render(request, "forms/Base_Form.html", {
                        "type": "study",
                        "object": None
                    })
                
                # Create study record
                study = FurtherStudy.objects.create(
                    alumni=alumni,
                    school_name=school_name,
                    program=program,
                    field_of_study=request.POST.get("field_of_study") or None,
                    status=status,
                    start_year=int(start_year),
                    end_year=int(request.POST.get("end_year")) if request.POST.get("end_year") else None,
                    is_ongoing=request.POST.get("is_ongoing") == "on",
                    description=request.POST.get("description") or None,
                    school_website=request.POST.get("school_website") or None,
                )
                
                # Log activity
                Activity.objects.create(
                    alumni=alumni,
                    activity_type="STUDY_ADD",
                    description=f"Added further studies: {program} at {school_name}"
                )
                
                messages.success(
                    request,
                    f"Further studies ({program}) added successfully!"
                )
                
                return redirect("account:alumni_dashboard")
                
        except ValueError as e:
            messages.error(request, "Please check your input values (especially years).")
            return render(request, "forms/Base_Form.html", {
                "type": "study",
                "object": None
            })
        except Exception as e:
            messages.error(request, f"Error saving study record: {str(e)}")
            return render(request, "forms/Base_Form.html", {
                "type": "study",
                "object": None
            })

    return render(request, "forms/Base_Form.html", {
        "type": "study",
        "object": None
    })

from django.db import transaction

@login_required
def edit_study(request, study_id):
    """Edit a further study record"""
    alumni = get_or_create_alumni_profile(request.user)

    # Get the study record
    study = get_object_or_404(FurtherStudy, id=study_id, alumni=alumni)

    if request.method == "POST":
        try:
            with transaction.atomic():
                # Validate required fields
                school_name = request.POST.get("school_name", "").strip()
                program = request.POST.get("program", "").strip()
                start_year = request.POST.get("start_year", "").strip()
                status = request.POST.get("status")

                # Validation
                if not school_name or not program or not start_year:
                    messages.error(request, "School, program, and start year are required.")
                    return render(request, "forms/Base_Form.html", {
                        "type": "study",
                        "object": study
                    })

                # Validate years
                try:
                    start_year_int = int(start_year)
                    end_year_int = None
                    if request.POST.get("end_year"):
                        end_year_int = int(request.POST.get("end_year"))
                        
                        # Validate logic
                        if start_year_int > end_year_int:
                            messages.error(request, "End year must be same or after start year.")
                            return render(request, "forms/Base_Form.html", {
                                "type": "study",
                                "object": study
                            })
                    
                    # Validate completion
                    if status == "COMPLETED" and not end_year_int:
                        messages.error(request, "End year required for completed programs.")
                        return render(request, "forms/Base_Form.html", {
                            "type": "study",
                            "object": study
                        })
                
                except ValueError:
                    messages.error(request, "Years must be valid numbers.")
                    return render(request, "forms/Base_Form.html", {
                        "type": "study",
                        "object": study
                    })

                # Update the record
                study.school_name = school_name
                study.program = program
                study.field_of_study = request.POST.get("field_of_study") or None
                study.status = status
                study.start_year = start_year_int
                study.end_year = end_year_int
                study.is_ongoing = request.POST.get("is_ongoing") == "on"
                study.description = request.POST.get("description") or None
                study.school_website = request.POST.get("school_website") or None
                study.save()

                # Log activity
                Activity.objects.create(
                    alumni=alumni,
                    activity_type="STUDY_UPDATE",
                    description=f"Updated further studies: {program}"
                )

                messages.success(request, f"{program} updated successfully!")
                return redirect("account:alumni_dashboard")

        except Exception as e:
            messages.error(request, f"Error updating study: {str(e)}")
            return render(request, "forms/Base_Form.html", {
                "type": "study",
                "object": study
            })

    return render(request, "forms/Base_Form.html", {
        "type": "study",
        "object": study
    })


@login_required
def delete_study(request, study_id):
    """Delete a further study record (POST only; modal + toast from dashboard/forms)."""
    alumni = get_or_create_alumni_profile(request.user)
    study = get_object_or_404(FurtherStudy, id=study_id, alumni=alumni)

    if request.method != "POST":
        messages.info(request, "Use the delete button on your dashboard to remove a study record.")
        return redirect("account:alumni_dashboard")

    try:
        program_name = study.program
        study.delete()
        Activity.objects.create(
            alumni=alumni,
            activity_type="STUDY_DELETE",
            description=f"Deleted further study: {program_name}",
        )
        if _wants_json(request):
            return JsonResponse({"ok": True, "message": f"{program_name} was deleted."})
        messages.success(request, f"{program_name} deleted successfully!")
    except Exception as e:
        if _wants_json(request):
            return JsonResponse({"ok": False, "message": str(e)}, status=400)
        messages.error(request, f"Error deleting study: {str(e)}")
    return redirect("account:alumni_dashboard")


@login_required
def edit_alumni_profile(request):
    """Update alumni profile fields and photo (glass UI)."""
    alumni = get_or_create_alumni_profile(request.user)
    programs = Program.objects.filter(is_active=True).order_by("order", "code")
    current_year = datetime.now().year
    graduation_years = list(range(current_year, 1950, -1))

    program_names = list(
        programs.values_list("full_name", flat=True)
    )
    extra_program = None
    if (
        alumni.program
        and str(alumni.program).strip()
        and alumni.program not in program_names
    ):
        extra_program = alumni.program

    if request.method == "POST":
        alumni.contact_number = request.POST.get("contact_number", "").strip() or None
        prog = request.POST.get("program", "").strip()
        if prog:
            alumni.program = prog
        gy = request.POST.get("graduation_year", "").strip()
        if gy:
            try:
                y = int(gy)
                if 1950 <= y <= current_year + 8:
                    alumni.graduation_year = y
            except ValueError:
                pass
        alumni.current_job_title = request.POST.get("current_job_title", "").strip() or None
        alumni.current_company = request.POST.get("current_company", "").strip() or None
        sen = request.POST.get("seniority_level", "").strip()
        if sen in dict(Alumni.SENIORITY_LEVEL):
            alumni.seniority_level = sen

        if request.POST.get("clear_photo"):
            if alumni.profile_photo:
                try:
                    alumni.profile_photo.delete(save=False)
                except OSError:
                    pass
                alumni.profile_photo = None
        elif "profile_photo" in request.FILES:
            alumni.profile_photo = request.FILES["profile_photo"]

        alumni.save()
        Activity.objects.create(
            alumni=alumni,
            activity_type="PROFILE_UPDATE",
            description="Updated profile from edit page",
        )
        messages.success(request, "Profile updated successfully.")
        return redirect("account:alumni_dashboard")

    return render(
        request,
        "account/Edit_Alumni_Profile.html",
        {
            "alumni": alumni,
            "programs": programs,
            "extra_program": extra_program,
            "graduation_years": graduation_years,
            "seniority_choices": Alumni.SENIORITY_LEVEL,
        },
    )

@login_required
def get_alumni_dashboard_context(alumni):
    """
    Helper function to gather all data needed for alumni dashboard
    Returns a context dictionary with all necessary information
    """
    current_employment = alumni.get_current_employment()
    all_employments = alumni.employments.all()
    further_studies = alumni.further_studies.all()
    recent_activities = alumni.activities.all()[:5]
    
    # Get career timeline data (all employments ordered by date)
    career_timeline = alumni.employments.all().order_by('-date_hired')
    
    # Calculate career duration statistics
    total_years_employed = 0
    first_job_date = None
    latest_job_date = None
    
    if career_timeline.exists():
        # Get first job (oldest)
        first_job = career_timeline.last()
        if first_job and first_job.date_hired:
            first_job_date = first_job.date_hired
        
        # Get current/latest job
        latest_job = career_timeline.first()
        if latest_job and latest_job.date_hired:
            latest_job_date = latest_job.date_hired
            
            # Calculate total years of experience if there's a start date
            if first_job_date:
                from datetime import date
                end_date = date.today() if not latest_job.date_left else latest_job.date_left
                total_years_employed = (end_date.year - first_job_date.year)
    
    context = {
        'alumni': alumni,
        'profile_completion': alumni.get_profile_completion_percentage(),
        'missing_fields': alumni.get_missing_profile_fields(),
        'profile_checklist': alumni.get_profile_checklist(),
        'employment_count': alumni.get_employment_count(),
        'current_employment': current_employment,
        'all_employments': all_employments,
        'further_studies': further_studies,
        'recent_activities': recent_activities,
        'years_since_graduation': alumni.get_years_since_graduation(),
        'career_timeline': career_timeline,
        'total_years_employed': total_years_employed,
        'first_job_date': first_job_date,
        'latest_job_date': latest_job_date,
        'section': 'dashboard',
    }
    
    return context


# ===============================
# 🧾 LEGAL PAGES
# ===============================
def terms_and_conditions(request):
    """
    Toast-style Terms & Conditions page (static content).
    """
    return render(request, "account/TERMS_AND_CONDITIONS.html", {})


def privacy_policy(request):
    """
    Toast-style Privacy Policy page (static content).
    """
    return render(request, "account/PRIVACY_POLICY.html", {})