from django.db import models

class Alumni(models.Model):
    EMPLOYMENT_STATUS = [
        ("EMPLOYED", "Employed"),
        ("UNEMPLOYED", "Unemployed"),
        ("SELF_EMPLOYED", "Self-employed"),
        ("STUDENT", "Further Studies"),
        ("UNKNOWN", "Unknown"),
    ]

    student_id = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField(blank=True, null=True)
    contact_number = models.CharField(max_length=30, blank=True, null=True)

    program = models.CharField(max_length=120)  # ex: BSIT
    graduation_year = models.PositiveIntegerField()

    employment_status = models.CharField(
        max_length=20, choices=EMPLOYMENT_STATUS, default="UNKNOWN"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.last_name}, {self.first_name} ({self.student_id})"


class Employment(models.Model):
    alumni = models.ForeignKey(Alumni, on_delete=models.CASCADE, related_name="employments")
    company_name = models.CharField(max_length=200)
    job_title = models.CharField(max_length=200)
    date_hired = models.DateField(blank=True, null=True)

    is_job_related = models.BooleanField(default=False)  # related to degree
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    employment_type = models.CharField(max_length=100, blank=True, null=True)  # full-time/part-time/contract

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.alumni} - {self.job_title} @ {self.company_name}"


class FurtherStudy(models.Model):
    alumni = models.ForeignKey(Alumni, on_delete=models.CASCADE, related_name="further_studies")
    school_name = models.CharField(max_length=200)
    program = models.CharField(max_length=200)  # Masters, certifications, etc.
    start_year = models.PositiveIntegerField(blank=True, null=True)
    end_year = models.PositiveIntegerField(blank=True, null=True)
    is_ongoing = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.alumni} - {self.program}"
