"""
Django Admin Configuration for T.I.P.ians Connect
Provides a user-friendly interface to manage all homepage content
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import CarouselSlide, CoreValue, PageContent, SiteConfig


@admin.register(CarouselSlide)
class CarouselSlideAdmin(admin.ModelAdmin):
    """
    Admin interface for managing carousel slides
    Shows preview of images and allows drag-and-drop ordering
    """
    
    list_display = ('slide_position', 'title_display', 'order', 'status_badge', 'preview_thumbnail')
    list_display_links = ('slide_position', 'title_display')
    list_editable = ('order',)
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'subtitle', 'description')
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'subtitle', 'description')
        }),
        ('Image', {
            'fields': ('background_image', 'image_preview'),
        }),
        ('Primary Button', {
            'fields': ('primary_button_text', 'primary_button_url'),
        }),
        ('Secondary Button (Optional)', {
            'fields': ('secondary_button_text', 'secondary_button_url'),
            'classes': ('collapse',)
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active'),
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def slide_position(self, obj):
        return f"Slide {obj.order}"
    slide_position.short_description = "Position"
    slide_position.admin_order_field = "order"

    def title_display(self, obj):
        return f"{obj.title} {obj.subtitle}"
    title_display.short_description = "Title"

    def status_badge(self, obj):
        if obj.is_active:
            color = '#28a745'
            text = 'Active'
        else:
            color = '#dc3545'
            text = 'Inactive'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            color,
            text
        )
    status_badge.short_description = "Status"

    def image_preview(self, obj):
        if obj.background_image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 100%; border-radius: 5px;" />',
                obj.background_image.url
            )
        return "No image uploaded"
    image_preview.short_description = "Image Preview"

    def preview_thumbnail(self, obj):
        if obj.background_image:
            return format_html(
                '<img src="{}" style="height: 40px; width: 60px; object-fit: cover; border-radius: 3px;" />',
                obj.background_image.url
            )
        return "-"
    preview_thumbnail.short_description = "Thumbnail"


@admin.register(CoreValue)
class CoreValueAdmin(admin.ModelAdmin):
    """
    Admin interface for managing core values
    Easy icon selection and ordering
    """
    
    list_display = ('value_position', 'title', 'icon_display', 'status_badge')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Value Information', {
            'fields': ('title', 'icon_class', 'description')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active'),
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def value_position(self, obj):
        return f"#{obj.order}"
    value_position.short_description = "Position"
    value_position.admin_order_field = "order"

    def icon_display(self, obj):
        return format_html(
            '<i class="{}"></i> {}',
            obj.icon_class,
            obj.get_icon_class_display()
        )
    icon_display.short_description = "Icon"

    def status_badge(self, obj):
        if obj.is_active:
            color = '#28a745'
            text = 'Active'
        else:
            color = '#dc3545'
            text = 'Inactive'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            color,
            text
        )
    status_badge.short_description = "Status"


@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    """
    Admin interface for managing page content sections
    Simple text editor for each section
    """
    
    list_display = ('section_display', 'content_preview', 'updated_at')
    list_filter = ('section', 'updated_at')
    readonly_fields = ('updated_at', 'section')
    
    fieldsets = (
        ('Section', {
            'fields': ('section',),
            'description': 'Select which section to edit'
        }),
        ('Title', {
            'fields': ('title',),
            'classes': ('collapse',)
        }),
        ('Content', {
            'fields': ('content',),
            'description': 'Edit the text content for this section'
        }),
        ('Metadata', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )

    def section_display(self, obj):
        return obj.get_section_display()
    section_display.short_description = "Section"

    def content_preview(self, obj):
        preview = obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
        return preview
    content_preview.short_description = "Content Preview"


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    """
    Admin interface for global site configuration
    Only one instance should exist (singleton)
    """
    list_display = ('site_name', 'logo_preview')
    readonly_fields = ('logo_preview',)
    
    def logo_preview(self, obj):
        if obj.logo_main:
            return format_html('<img src="{}" style="max-height:60px;"/>', obj.logo_main.url)
        return "(No logo)"
    logo_preview.short_description = 'Logo preview'
    # Prevent adding or deleting
    def has_add_permission(self, request):
        return not SiteConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = ('company_name', 'copyright_year')
    readonly_fields = ('updated_at',)
    
    fieldsets = (
        ('Company Information', {
            'fields': ('company_name', 'tagline','logo_main', 'copyright_year')
        }),
        ('Branding Colors', {
            'fields': ('primary_color', 'secondary_color'),
            'description': 'Use hexadecimal format: #RRGGBB (e.g., #FFD700 for gold)'
        }),
        ('Metadata', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )

from .models import Program, EmploymentStatus, Feature, RegistrationPageContent


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('code', 'full_name', 'is_active', 'order')
    list_filter = ('is_active', 'created_at')
    search_fields = ('code', 'full_name')
    ordering = ('order', 'code')
    
    fieldsets = (
        ('Program Information', {
            'fields': ('code', 'full_name')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active'),
            'description': 'Order determines display sequence in dropdown (lower = first). Inactive programs won\'t appear.'
        }),
    )


@admin.register(EmploymentStatus)
class EmploymentStatusAdmin(admin.ModelAdmin):
    list_display = ('label', 'value', 'is_active', 'order')
    list_filter = ('is_active', 'created_at')
    search_fields = ('label', 'value')
    ordering = ('order',)
    
    fieldsets = (
        ('Status Information', {
            'fields': ('value', 'label')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active'),
            'description': 'Value is the database key, Label is what users see.'
        }),
    )


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'is_active', 'order')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('order',)
    
    fieldsets = (
        ('Feature Information', {
            'fields': ('title', 'description')
        }),
        ('Display Settings', {
            'fields': ('icon', 'order', 'is_active'),
            'description': 'Icon: Font Awesome class (e.g., "fas fa-network-wired"). See: https://fontawesome.com/icons'
        }),
    )


@admin.register(RegistrationPageContent)
class RegistrationPageContentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'updated_at')
    
    fieldsets = (
        ('Hero Section', {
            'fields': ('hero_title', 'hero_tagline', 'hero_description'),
            'description': 'Content shown on the left side of registration page'
        }),
        ('Form Section', {
            'fields': ('form_title', 'form_subtitle', 'login_text'),
            'description': 'Content shown on the registration form'
        }),
    )
    
    def has_add_permission(self, request):
        """Limit to single instance"""
        return not RegistrationPageContent.objects.exists()