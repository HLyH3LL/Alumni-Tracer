from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .models1 import CarouselSlide, CoreValue, PageContent, SiteConfig

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

    PROGRAMS = [
        ("BS CS", "BS Computer Science"),
        ("BS CpE", "BS Computer Engineering"),
        ("BS ECE", "BS Electronics Engineering"),
        ("BS EE", "BS Electrical Engineering"),
        ("BS ME", "BS Mechanical Engineering"),
        ("BS CE","BS Civil Engineering"),
        ("BS Arch","BS Architecture"),
        ("BS IE","BS Industrial Engineering"),
        ("BS Accountancy","BS Accountancy"),
        ("BS BA","BS Business Administration"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='alumni_profile', null=True, blank=True)
    
    student_id = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField(blank=True, null=True)
    contact_number = models.CharField(max_length=30, blank=True, null=True)

    program = models.CharField(max_length=120)
    graduation_year = models.PositiveIntegerField()

    is_verified = models.BooleanField(default=False)

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

    is_verified = models.BooleanField(
        default=False,
        help_text="Set True when alumni information is verified (e.g. by admin).",
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
 
    def get_profile_checklist(self):
        """Goal items for dashboard progress (same basis as completion %)."""
        items = []

        def add_row(key, label, done, optional=False):
            items.append(
                {"key": key, "label": label, "done": bool(done), "optional": optional}
            )

        add_row("photo", "Upload a profile photo", self.profile_photo)
        add_row(
            "contact",
            "Add your contact number",
            self.contact_number and str(self.contact_number).strip(),
        )
        program_ok = (
            self.program
            and str(self.program).strip()
            and self.program != "Not Specified"
        )
        add_row(
            "program_year",
            "Set your program and graduation year",
            program_ok and bool(self.graduation_year),
        )
        add_row(
            "job_title",
            "Add your current job title",
            self.current_job_title and str(self.current_job_title).strip(),
        )
        add_row(
            "company",
            "Add your current company",
            self.current_company and str(self.current_company).strip(),
        )
        add_row(
            "seniority",
            "Set your seniority level (not “Unknown”)",
            self.seniority_level and self.seniority_level != "UNKNOWN",
        )
        add_row(
            "timeline",
            "Add at least one job to your career timeline",
            self.employments.exists(),
        )
        add_row(
            "studies",
            "Record further studies (optional)",
            self.further_studies.exists(),
            optional=True,
        )
        return items

    def get_profile_completion_percentage(self):
        """Percent of checklist items completed."""
        items = self.get_profile_checklist()
        if not items:
            return 0
        done = sum(1 for i in items if i["done"])
        return int(round(100 * done / len(items)))

    def get_missing_profile_fields(self):
        """Human-readable labels for incomplete checklist items."""
        return [i["label"] for i in self.get_profile_checklist() if not i["done"]]
 
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

    is_job_related = models.BooleanField(default=False)
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    employment_type = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_via_voice = models.BooleanField(default=False)
    voice_transcript = models.TextField(blank=True, null=True)
    voice_updated = models.BooleanField(default=False)

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
    created_via_voice = models.BooleanField(default=False)
    voice_transcript = models.TextField(blank=True, null=True)
    voice_updated = models.BooleanField(default=False)
    
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
        ("EMPLOYMENT_DELETE", "Employment Deleted"),
        ("STUDY_ADD", "Study Added"),
        ("STUDY_UPDATE", "Study Updated"),
        ("STUDY_DELETE", "Study Deleted"),
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

from django.db import models
from django.contrib.auth.models import User

class Program(models.Model):
    """Store all academic programs - replaces hardcoded dropdown"""
    code = models.CharField(max_length=20, unique=True) 
    full_name = models.CharField(max_length=100) 
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'code']
        verbose_name = "Program"
        verbose_name_plural = "Programs"
    
    def __str__(self):
        return f"{self.code} - {self.full_name}"


class EmploymentStatus(models.Model):
    value = models.CharField(max_length=20, unique=True) 
    label = models.CharField(max_length=50)  
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Employment Status"
        verbose_name_plural = "Employment Statuses"
    
    def __str__(self):
        return self.label


class Feature(models.Model):
    """Store registration page features - replaces hardcoded features"""
    title = models.CharField(max_length=50)  # "Network"
    description = models.TextField()  # "Connect with fellow alumni..."
    icon = models.CharField(max_length=100, default="fas fa-network-wired")  # Font Awesome
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Feature"
        verbose_name_plural = "Features"
    
    def __str__(self):
        return self.title


class RegistrationPageContent(models.Model):
    """Store all registration page text content"""
    # Hero Section
    hero_title = models.CharField(
        max_length=200, 
        default="WELCOME TO THE T.I.P.ian ALUMNI COMMUNITY"
    )
    hero_tagline = models.CharField(
        max_length=200, 
        default="Your professional network starts here!"
    )
    hero_description = models.TextField(
        default="Join thousands of T.I.P Manila alumni and expand your professional horizons. Connect, collaborate, and grow with our thriving community."
    )
    
    # Form Section
    form_title = models.CharField(
        max_length=100, 
        default="ALUMNI REGISTRATION"
    )
    form_subtitle = models.CharField(
        max_length=200, 
        default="Join the T.I.P Manila Alumni Community"
    )
    login_text = models.CharField(
        max_length=100, 
        default="Already have an account?"
    )
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Registration Page Content"
        verbose_name_plural = "Registration Page Content"
    
    def __str__(self):
        return "Registration Page Configuration"
    
class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title