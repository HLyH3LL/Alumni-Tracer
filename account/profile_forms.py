from django import forms
from django.contrib.auth.models import User
from .models import Alumni, Employment, FurtherStudy


class AlumniProfileForm(forms.ModelForm):
    """Form for updating alumni profile information"""
    
    class Meta:
        model = Alumni
        fields = [
            'first_name', 'last_name', 'email', 'contact_number',
            'tip_email', 'bio', 'profile_photo',
            'current_job_title', 'current_company', 'seniority_level',
            'linkedin_url', 'facebook_url', 'instagram_url', 
            'github_url', 'personal_website'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'tip_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'TIP Institutional Email'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Short biography about yourself',
                'rows': 4
            }),
            'profile_photo': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'current_job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your current job title'
            }),
            'current_company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your current company'
            }),
            'seniority_level': forms.Select(attrs={
                'class': 'form-control'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/yourprofile'
            }),
            'facebook_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://facebook.com/yourprofile'
            }),
            'instagram_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://instagram.com/yourprofile'
            }),
            'github_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/yourprofile'
            }),
            'personal_website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourwebsite.com'
            }),
        }


class EmploymentForm(forms.ModelForm):
    """Form for adding/editing employment records"""
    
    class Meta:
        model = Employment
        fields = [
            'company_name', 'job_title', 'seniority_level',
            'employment_type', 'salary_range', 'is_current',
            'is_job_related', 'date_hired', 'date_left',
            'job_description', 'location', 'company_website'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company Name'
            }),
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Job Title'
            }),
            'seniority_level': forms.Select(attrs={
                'class': 'form-control'
            }),
            'employment_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'salary_range': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_current': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_job_related': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'date_hired': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'date_left': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'job_description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your responsibilities and achievements',
                'rows': 4
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, Country'
            }),
            'company_website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://company-website.com'
            }),
        }


class FurtherStudyForm(forms.ModelForm):
    """Form for adding/editing further study records"""
    
    class Meta:
        model = FurtherStudy
        fields = [
            'school_name', 'program', 'program_level',
            'field_of_study', 'status',
            'start_year', 'end_year',
            'description', 'school_website'
        ]
        widgets = {
            'school_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'School/University Name'
            }),
            'program': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Program Name'
            }),
            'program_level': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "e.g., Master's Degree, Certification"
            }),
            'field_of_study': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "e.g., Computer Science"
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'start_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '2020',
                'min': '1950',
                'max': '2100'
            }),
            'end_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '2023',
                'min': '1950',
                'max': '2100'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Additional details about your studies',
                'rows': 4
            }),
            'school_website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://school-website.com'
            }),
        }


class NetworkForm(forms.ModelForm):
    """Form for connecting social networks"""
    
    class Meta:
        model = Network
        fields = ['profile_url']
        widgets = {
            'profile_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your profile URL'
            }),
        }


class EmploymentFilterForm(forms.Form):
    """Form for filtering employment records"""
    
    STATUS = [
        ('', 'All Statuses'),
        ('True', 'Current'),
        ('False', 'Previous'),
    ]
    
    SENIORITY = [
        ('', 'All Levels'),
        ('ENTRY', 'Entry Level'),
        ('JUNIOR', 'Junior Level'),
        ('SENIOR', 'Senior Level'),
        ('LEAD', 'Lead/Manager'),
        ('DIRECTOR', 'Director/Executive'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    seniority_level = forms.ChoiceField(
        choices=SENIORITY,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by company or job title'
        })
    )


class StudyFilterForm(forms.Form):
    """Form for filtering study records"""
    
    STATUS = [
        ('', 'All Status'),
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed'),
        ('DISCONTINUED', 'Discontinued'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by school or program'
        })
    )


class AlumniSearchForm(forms.Form):
    """Form for admin to search/filter alumni"""
    
    STATUSES = [
        ('', 'All Statuses'),
        ('EMPLOYED', 'Employed'),
        ('UNEMPLOYED', 'Unemployed'),
        ('SELF_EMPLOYED', 'Self-employed'),
        ('STUDENT', 'Studying'),
    ]
    
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, email, or student ID',
            'aria-label': 'Search alumni'
        })
    )
    
    employment_status = forms.ChoiceField(
        choices=STATUSES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'aria-label': 'Filter by employment status'
        })
    )
    
    program = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by program (e.g., BSIT)',
            'aria-label': 'Filter by program'
        })
    )