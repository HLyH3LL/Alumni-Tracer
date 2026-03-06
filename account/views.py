from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User  # This is important!

from .Loginforms import LoginForm
from .Registerforms import UserProfileForm, AlumniProfileForm
from .models import Alumni

@login_required
def dashboard(request):
    return render(request, "account/dashboard.html", {"section": "dashboard"})


# staff-only decorator
def staff_required(view_func):
    return login_required(user_passes_test(lambda u: u.is_staff)(view_func))


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
                    return redirect("account:dashboard")

                return HttpResponse("Disabled account")

            return HttpResponse("Invalid login")

    else:
        form = LoginForm()

    return render(request, "registration/login.html", {"form": form})


@login_required
def account_view(request):
    """View and edit user account/profile"""
    user = request.user
    
    # Try to get alumni profile if it exists
    try:
        alumni = user.alumni
    except Alumni.DoesNotExist:
        alumni = None
        messages.warning(request, 'Please complete your alumni profile.')
    
    if request.method == 'POST':
        # Handle profile update
        if 'update_profile' in request.POST:
            user_form = UserProfileForm(request.POST, instance=user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('account:account')
        
        # Handle alumni details update
        elif 'update_alumni' in request.POST:
            if alumni:
                alumni_form = AlumniProfileForm(request.POST, request.FILES, instance=alumni)
            else:
                # Create new alumni profile if it doesn't exist
                alumni_form = AlumniProfileForm(request.POST, request.FILES)
                
            if alumni_form.is_valid():
                alumni = alumni_form.save(commit=False)
                alumni.user = user
                alumni.save()
                messages.success(request, 'Your alumni details have been updated successfully!')
                return redirect('account:account')
    
    user_form = UserProfileForm(instance=user)
    alumni_form = AlumniProfileForm(instance=alumni) if alumni else AlumniProfileForm()
    
    context = {
        'user_form': user_form,
        'alumni_form': alumni_form,
        'alumni': alumni,
        'section': 'account'
    }
    return render(request, 'account/account.html', context)


@login_required
def change_password(request):
    """Handle password change"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('account:account')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'account/change_password.html', {
        'form': form,
        'section': 'account'
    })


def register(request):
    """Register a new user"""
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'registration/register.html')
        
        # Create username from first and last name
        # Format: firstname.lastname (lowercase, no spaces)
        base_username = f"{first_name.lower()}.{last_name.lower()}"
        username = base_username
        
        # Handle duplicate usernames by adding numbers
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'registration/register.html')
        
        # Create user (non-staff, non-superuser)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )
        user.is_staff = False
        user.is_superuser = False
        user.save()
        
        messages.success(request, f'Account created successfully! Your username is: {username}')
        return redirect('account:login')
    
    return render(request, 'registration/register.html')