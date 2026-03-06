from django.db import models
from django.contrib.auth.models import User

class Alumni(models.Model):
    EMPLOYMENT_STATUS_CHOICES = [
        ('employed', 'Employed'),
        ('unemployed', 'Unemployed'),
        ('self-employed', 'Self-Employed'),
        ('student', 'Student'),
        ('other', 'Other'),
    ]
    
    PROGRAM_CHOICES = [
    ('BSCS', 'Bachelor of Science in Computer Science'),
    ('BSIT', 'Bachelor of Science in Information Technology'),
    ('BSE', 'Bachelor of Science in Education'),
    # Add other programs here
]
    
    # Link to User model
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='alumni')
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    
    # Alumni Details - ADD THESE MISSING FIELDS
    program = models.CharField(max_length=100, choices=PROGRAM_CHOICES)
    graduation_year = models.IntegerField()
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, blank=True, null=True)
    company = models.CharField(max_length=200, blank=True, null=True)  
    position = models.CharField(max_length=100, blank=True, null=True)  
    bio = models.TextField(blank=True, null=True)  
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)  
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
from django.db import models
from django.contrib.auth.models import User

class Alumni(models.Model):
    EMPLOYMENT_STATUS_CHOICES = [
        ('employed', 'Employed'),
        ('unemployed', 'Unemployed'),
        ('self-employed', 'Self-Employed'),
        ('student', 'Student'),
        ('other', 'Other'),
    ]
    
    # Link to User model
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='alumni')
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    
    # Alumni Details
    program = models.CharField(max_length=120)  # ex: BSIT
    graduation_year = models.IntegerField()
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, blank=True, null=True)
    company = models.CharField(max_length=200, blank=True, null=True)  
    position = models.CharField(max_length=100, blank=True, null=True)  
    bio = models.TextField(blank=True, null=True)  
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)  
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.program} ({self.graduation_year})"
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.program} ({self.graduation_year})"
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}"