from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from datetime import datetime
from .models import Alumni, Program, EmploymentStatus
import re

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter your Student ID.'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password.'})
    )

class AlumniRegistrationForm(UserCreationForm):
    student_id = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., 2012345'})
    )
    first_name = forms.CharField(
        max_length=80,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter first name.'})
    )
    last_name = forms.CharField(
        max_length=80,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter last name.'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'your.email@example.com'})
    )
    contact_number = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., 0917-123-4567'})
    )
    program = forms.ChoiceField(choices=[('', 'Select Program')], required=True)
    graduation_year = forms.ChoiceField(choices=[('', 'Select Year')], required=True)
    employment_status = forms.ChoiceField(choices=[('', 'Select Status')], required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Keep form choices aligned with the registration page dropdowns.
        current_year = datetime.now().year
        self.fields['graduation_year'].choices = [('', 'Select Year')] + [
            (str(year), str(year)) for year in range(current_year, 2010, -1)
        ]

        program_choices = [('', 'Select Program')] + [
            (p.full_name, p.full_name) for p in Program.objects.filter(is_active=True).order_by('order', 'code')
        ]
        self.fields['program'].choices = program_choices

        employment_choices = [('', 'Select Status')] + [
            (s.value, s.label) for s in EmploymentStatus.objects.filter(is_active=True).order_by('order')
        ]
        self.fields['employment_status'].choices = employment_choices
      
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Create a password',
            'class': 'form-control'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm password',
            'class': 'form-control'
        })
        
        self.fields['password1'].help_text = 'At least 8 characters'
        self.fields['password2'].help_text = ''

    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
    
        if student_id and not re.match(r'^\d{7}$', student_id):
            raise forms.ValidationError('Student ID must be 7 digits (e.g., YY12345)')
    
        if Alumni.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError('This Student ID is already registered.')
        return student_id

    def clean_email(self):
        """Check if email is already used"""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def save(self, commit=True):
        """Save both User and Alumni objects"""
        user = User.objects.create_user(
            username=self.cleaned_data['student_id'],
            password=self.cleaned_data['password1'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        
        if commit:
            user.save()
            
            alumni = Alumni.objects.create(
                user=user, 
                student_id=self.cleaned_data['student_id'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                email=self.cleaned_data['email'],
                contact_number=self.cleaned_data['contact_number'],
                program=self.cleaned_data['program'],
                graduation_year=self.cleaned_data['graduation_year'],
                employment_status=self.cleaned_data['employment_status']
            )
        
        return user