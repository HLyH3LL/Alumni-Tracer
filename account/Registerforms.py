from django import forms
from django.contrib.auth.models import User
from .models import Alumni


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile"""
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your first name'
    }))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your last name'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email'
    }))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class AlumniProfileForm(forms.ModelForm):
    """Form for editing alumni profile"""
    class Meta:
        model = Alumni
        fields = ['program', 'graduation_year', 'employment_status', 
                  'company', 'position', 'bio', 'profile_picture', 'contact_number']
        widgets = {
            'program': forms.Select(attrs={'class': 'form-control'}),
            'graduation_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1950,
                'max': 2030
            }),
            'employment_status': forms.Select(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your company'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your position'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself'
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your contact number'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control-file'
            }),
        }