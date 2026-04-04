from django.db import models

class CarouselSlide(models.Model):
    """
    Manage carousel slides dynamically
    Matches the 3 hero slides in the carousel
    """
    title = models.CharField(
        max_length=100,
        help_text="Main text (e.g., 'Connect With Your')"
    )
    subtitle = models.CharField(
        max_length=100,
        help_text="Golden highlighted text (e.g., 'Alumni Community')"
    )
    description = models.TextField(
        help_text="Slide description paragraph"
    )
    background_image = models.ImageField(
        upload_to='carousel/',
        help_text="Background image for the slide"
    )
    
    # Primary CTA Button
    primary_button_text = models.CharField(
        max_length=100,
        help_text="Primary button label (e.g., 'Learn More')"
    )
    primary_button_url = models.CharField(
        max_length=255,
        help_text="Where primary button links to"
    )
    
    # Secondary CTA Button (optional)
    secondary_button_text = models.CharField(
        max_length=100,
        blank=True,
        help_text="Secondary button label (optional)"
    )
    secondary_button_url = models.CharField(
        max_length=255,
        blank=True,
        help_text="Where secondary button links to (optional)"
    )
    
    # Display order (1, 2, 3...)
    order = models.PositiveIntegerField(
        default=0,
        help_text="Slide position (lower numbers appear first)"
    )
    
    # Control visibility
    is_active = models.BooleanField(
        default=True,
        help_text="Only active slides appear on the homepage"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Carousel Slide"
        verbose_name_plural = "Carousel Slides"

    def __str__(self):
        return f"Slide {self.order}: {self.title}"


class CoreValue(models.Model):
    """
    Store the 6 core values displayed in the values grid
    Community, Innovation, Excellence, Integrity, Inclusivity, Growth
    """
    
    # FontAwesome icon classes
    ICON_CHOICES = (
        ('fas fa-handshake', 'Handshake (Community)'),
        ('fas fa-lightbulb', 'Lightbulb (Innovation)'),
        ('fas fa-chart-line', 'Chart Line (Excellence)'),
        ('fas fa-users', 'Users (Integrity)'),
        ('fas fa-globe', 'Globe (Inclusivity)'),
        ('fas fa-rocket', 'Rocket (Growth)'),
        ('fas fa-heart', 'Heart'),
        ('fas fa-star', 'Star'),
        ('fas fa-brain', 'Brain'),
        ('fas fa-shield-alt', 'Shield'),
        ('fas fa-target', 'Target'),
        ('fas fa-crown', 'Crown'),
    )
    
    title = models.CharField(
        max_length=50,
        help_text="Value name (e.g., 'Community')"
    )
    
    icon_class = models.CharField(
        max_length=50,
        choices=ICON_CHOICES,
        help_text="Choose an icon for this value"
    )
    
    description = models.TextField(
        help_text="Description of this core value"
    )
    
    # Display order
    order = models.PositiveIntegerField(
        default=0,
        help_text="Position in the values grid"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Only active values appear on homepage"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Core Value"
        verbose_name_plural = "Core Values"

    def __str__(self):
        return f"{self.order}. {self.title}"


class PageContent(models.Model):
    """
    Store text content for different page sections
    - About Hero section
    - Mission statement
    - Vision statement
    """
    
    SECTION_CHOICES = (
        ('about_hero', 'About Section - Hero Title'),
        ('about_description', 'About Section - Description'),
        ('mission', 'Mission Statement'),
        ('vision', 'Vision Statement'),
    )
    
    section = models.CharField(
        max_length=50,
        choices=SECTION_CHOICES,
        unique=True,
        help_text="Which section this content belongs to"
    )
    
    title = models.CharField(
        max_length=300,
        blank=True,
        help_text="Section title (if applicable)"
    )
    
    content = models.TextField(
        help_text="Main content text"
    )
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Page Content"
        verbose_name_plural = "Page Content"

    def __str__(self):
        return self.get_section_display()


class SiteConfig(models.Model):
    """
    Global site configuration - company info, colors, etc.
    Only one instance should exist (singleton pattern)
    """
    
    # Company Information
    company_name = models.CharField(
        max_length=200,
        default="Technological Institute of the Philippines - Manila"
    )
    
    tagline = models.CharField(
        max_length=255,
        default="T.I.P.ians Connect: Alumni Tracer System for IT Graduates"
    )
    
    # Branding Colors (in hex format)
    primary_color = models.CharField(
        max_length=7,
        default="#FFD700",
        help_text="Primary brand color (gold) - use hex format #RRGGBB"
    )
    
    secondary_color = models.CharField(
        max_length=7,
        default="#28282B",
        help_text="Secondary brand color (dark) - use hex format"
    )
    
    # Copyright Year
    copyright_year = models.IntegerField(
        default=2024,
        help_text="Year for copyright notice"
    )
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"

    def __str__(self):
        return "Site Configuration"

    @classmethod
    def get_config(cls):
        """Get or create the single config instance"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if self.pk is None:
            self.pk = 1
        super().save(*args, **kwargs)

    logo_main = models.ImageField(upload_to='logos/', blank=True, null=True)     # header logo
    logo_footer = models.ImageField(upload_to='logos/', blank=True, null=True)   # footer logo
    favicon = models.ImageField(upload_to='logos/', blank=True, null=True)       # favicon
    # ...existing code...