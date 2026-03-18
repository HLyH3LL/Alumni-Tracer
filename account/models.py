from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Alumni(models.Model):
    EMPLOYMENT_STATUS = [
        ("EMPLOYED", "Employed"),
        ("UNEMPLOYED", "Unemployed"),
        ("SELF_EMPLOYED", "Self-employed"),
        ("STUDENT", "Further Studies"),
        ("UNKNOWN", "Unknown"),
    ]

    SENIORITY_LEVEL = [
        ("ENTRY", "Entry Level"),
        ("JUNIOR", "Junior Level"),
        ("SENIOR", "Senior Level"),
        ("LEAD", "Lead/Manager"),
        ("DIRECTOR", "Director/Executive"),
        ("UNKNOWN", "Unknown"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='alumni_profile', null=True, blank=True)
    
    student_id = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField(blank=True, null=True)
    contact_number = models.CharField(max_length=30, blank=True, null=True)

    program = models.CharField(max_length=120)
    graduation_year = models.PositiveIntegerField()

    profile_photo = models.ImageField(
        upload_to='alumni_photos/', 
        blank=True, 
        null=True
    )

    employment_status = models.CharField(
        max_length=20, choices=EMPLOYMENT_STATUS, default="UNKNOWN"
    )

    current_job_title = models.CharField(max_length=200, blank=True, null=True)
    current_company = models.CharField(max_length=200, blank=True, null=True)
    seniority_level = models.CharField(
        max_length=20,
        choices=SENIORITY_LEVEL,
        default="UNKNOWN"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-graduation_year', 'last_name', 'first_name']
        verbose_name_plural = "Alumni"
        indexes = [
            models.Index(fields=['student_id']),
            models.Index(fields=['graduation_year']),
            models.Index(fields=['employment_status']),
        ]
 
    def __str__(self):
        return f"{self.last_name}, {self.first_name} ({self.student_id})"
 
    def get_profile_completion_percentage(self):
        """Calculate profile completion percentage"""
        required_fields = [
            self.first_name,
            self.last_name,
            self.email,
            self.contact_number,
            self.program,
            self.graduation_year,
        ]
        optional_fields = [
            self.current_job_title,
            self.profile_photo,
        ]
        
        required_filled = sum(1 for field in required_fields if field)
        optional_filled = sum(1 for field in optional_fields if field)
        
        total_score = (required_filled / len(required_fields) * 75) + (optional_filled / len(optional_fields) * 25)
        return int(total_score)
 
    def get_missing_profile_fields(self):
        """Return list of missing important profile fields"""
        missing = []
        
        if not self.current_job_title or not self.current_company:
            missing.append("Current Job")
        if not self.profile_photo:
            missing.append("Profile Photo")
        
        return missing
 
    def get_employment_count(self):
        """Get total number of employment records"""
        return self.employments.count()
 
    def get_current_employment(self):
        """Get the most recent employment record"""
        return self.employments.order_by('-date_hired').first()
 
    def get_years_since_graduation(self):
        """Calculate years since graduation"""
        current_year = timezone.now().year
        return current_year - self.graduation_year

    def __str__(self):
        return f"{self.last_name}, {self.first_name} ({self.student_id})"


class Employment(models.Model):
    EMPLOYMENT_TYPE = [
        ("FULL_TIME", "Full-time"),
        ("PART_TIME", "Part-time"),
        ("CONTRACT", "Contract"),
        ("FREELANCE", "Freelance"),
        ("INTERNSHIP", "Internship"),
    ]

    alumni = models.ForeignKey(
        Alumni,
        on_delete=models.CASCADE,
        related_name="employments"
    )
    company_name = models.CharField(max_length=200)
    job_title = models.CharField(max_length=200)
    date_hired = models.DateField(blank=True, null=True)

    is_job_related = models.BooleanField(default=False)  # related to degree
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    employment_type = models.CharField(max_length=100, blank=True, null=True)  # full-time/part-time/contract

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.alumni} - {self.job_title} @ {self.company_name}"


class FurtherStudy(models.Model):
    STUDY_STATUS = [
        ("ONGOING", "Ongoing"),
        ("COMPLETED", "Completed"),
        ("DROPPED", "Dropped"),
    ]

    alumni = models.ForeignKey(
        Alumni,
        on_delete=models.CASCADE,
        related_name="further_studies"
    )
    school_name = models.CharField(max_length=200)
    program = models.CharField(max_length=200)  # Masters, certifications, etc.
    start_year = models.PositiveIntegerField(blank=True, null=True)
    end_year = models.PositiveIntegerField(blank=True, null=True)
    is_ongoing = models.BooleanField(default=True)

    status = models.CharField(
        max_length=20,
        choices=STUDY_STATUS,
        default="ONGOING"
    )
    
    field_of_study = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="e.g., Computer Science, Business Administration"
    )
    
    description = models.TextField(blank=True, null=True)
    school_website = models.URLField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_year']
        verbose_name_plural = "Further Studies"
        indexes = [
            models.Index(fields=['alumni', 'status']),
        ]
 
    def __str__(self):
        return f"{self.alumni} - {self.program}"
 
    def get_duration_display(self):
        """Get formatted duration for display"""
        start = self.start_year if self.start_year else "Unknown"
        end = "Present" if self.status == "ONGOING" else (self.end_year if self.end_year else "Unknown")
        return f"{start} - {end}"


class Activity(models.Model):
    ACTIVITY_TYPE = [
        ("PROFILE_UPDATE", "Profile Updated"),
        ("EMPLOYMENT_ADD", "Employment Added"),
        ("EMPLOYMENT_UPDATE", "Employment Updated"),
        ("STUDY_ADD", "Study Added"),
        ("LOGIN", "Login"),
        ("NETWORK_CONNECT", "Network Connected"),
        ("PROFILE_PHOTO_UPDATE", "Profile Photo Updated"),
    ]
 
    alumni = models.ForeignKey(
        Alumni,
        on_delete=models.CASCADE,
        related_name="activities"
    )
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPE)
    description = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Activities"
        indexes = [
            models.Index(fields=['alumni', 'created_at']),
        ]
 
    def __str__(self):
        return f"{self.alumni} - {self.get_activity_type_display()}"