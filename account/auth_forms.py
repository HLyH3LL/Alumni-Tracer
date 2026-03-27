from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
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
    program = forms.ModelChoiceField(
        queryset=Program.objects.filter(is_active=True),
        required=True,
        empty_label='Select Program'
    )
    graduation_year = forms.ChoiceField(
        choices=[('', 'Select Year')] + [(str(year), str(year)) for year in range(2024, 2009, -1)],
        required=True
    )
    employment_status = forms.ModelChoiceField(
        queryset=EmploymentStatus.objects.filter(is_active=True),
        required=True,
        empty_label='Select Status'
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
      
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

        if User.objects.filter(username=student_id).exists():
            raise forms.ValidationError('A user with this Student ID already exists.')

        return student_id

    def clean_email(self):
        """Check if email is already used"""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def save(self, commit=True):
        """Save both User and Alumni objects"""
        try:
            user = User.objects.create_user(
                username=self.cleaned_data['student_id'],
                password=self.cleaned_data['password1'],
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name']
            )
        except IntegrityError:
            raise forms.ValidationError('A user with this Student ID already exists.')

        if commit:
            user.save()
            
            program = self.cleaned_data['program']
            employment_status = self.cleaned_data['employment_status']
            try:
                alumni = Alumni.objects.create(
                    user=user,
                    student_id=self.cleaned_data['student_id'],
                    first_name=self.cleaned_data['first_name'],
                    last_name=self.cleaned_data['last_name'],
                    email=self.cleaned_data['email'],
                    contact_number=self.cleaned_data['contact_number'],
                    program=program.code if program else '',
                    graduation_year=self.cleaned_data['graduation_year'],
                    employment_status=employment_status.value if employment_status else ''
                )
            except Exception as e:
                user.delete()  # Clean up the user if alumni creation fails
                raise forms.ValidationError(f'Failed to create alumni profile: {str(e)}')
        
        return user


class AdminAlumniForm(forms.ModelForm):
    class Meta:
        model = Alumni
        fields = [
            'student_id',
            'first_name',
            'last_name',
            'email',
            'contact_number',
            'program',
            'graduation_year',
            'employment_status',
            'current_job_title',
            'current_company',
            'seniority_level',
            'is_verified'
        ]

    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        qs = Alumni.objects.filter(student_id=student_id)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('This Student ID is already in use.')
        return student_id
