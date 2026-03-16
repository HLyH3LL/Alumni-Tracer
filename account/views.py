from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from .forms import AlumniRegistrationForm 
from django.contrib import messages 

from .Loginforms import LoginForm
from .models import Alumni


@login_required
def dashboard(request):
    return render(request, "account/User_Dashboard.html", {"section": "dashboard"})


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
                        return redirect("account:dashboard")

                return HttpResponse("Disabled account")

            return HttpResponse("Invalid login")

    else:
        form = LoginForm()

    return render(request, "registration/User_Login.html", {"form": form})


def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == "POST":
        form = AlumniRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! You can now login with your Student ID.')
            return redirect('account:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AlumniRegistrationForm()
    
    return render(request, 'registration/User_Register.html', {'form': form})